"""
Views for live bidding system - including OTP auth, auction creation, and bidding
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import timedelta
import json
from decimal import Decimal

from livebidding.services import OTPService
from livebidding.models import (
    OTPVerification, AnonymousBidderId, BiddingRoom, BidAudit,
    AuctionWinner, AntiFraudLog, LivestockType, BiddingStats
)
from auctions.models import Auction
from products.models import Product
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


# ============ OTP Authentication Views ============

@csrf_exempt
@require_POST
def send_otp(request):
    """Send OTP to email address"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'success': False, 'message': 'Invalid email address'})
        
        result = OTPService.send_otp(email)
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@csrf_exempt
@require_POST
def verify_otp(request):
    """Verify OTP and log in user"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        otp_code = data.get('otp_code', '').strip()
        
        if not email or not otp_code:
            return JsonResponse({
                'success': False,
                'message': 'Email and OTP code are required'
            })
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'success': False, 'message': 'Invalid email address'})
        
        result = OTPService.verify_otp(email, otp_code)
        
        if result['success']:
            user = result['user']
            BiddingStats.objects.get_or_create(user=user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username,
            })
        else:
            return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


@csrf_exempt
@require_POST
def resend_otp(request):
    """Resend OTP to email address"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'success': False, 'message': 'Invalid email address'})
        
        result = OTPService.resend_otp(email)
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})
    except Exception as e:
        logger.error(f"Error resending OTP: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


# ============ Auction Listing Views ============

@login_required(login_url='otp_login')
def auction_list(request):
    """Display list of active auctions for bidding"""
    # Get active auctions
    auctions = Auction.objects.filter(
        status='active',
        is_active=True,
    ).select_related('product', 'seller').prefetch_related('bidding_room')
    
    # Filter by livestock type if provided
    livestock_type = request.GET.get('livestock_type')
    if livestock_type:
        auctions = auctions.filter(product__livestock_type__slug=livestock_type)
    
    # Filter by search query
    search_query = request.GET.get('q')
    if search_query:
        auctions = auctions.filter(product__title__icontains=search_query)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(auctions, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get livestock types for filter
    livestock_types = LivestockType.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'auctions': page_obj.object_list,
        'livestock_types': livestock_types,
        'search_query': search_query,
        'selected_type': livestock_type,
    }
    
    return render(request, 'livebidding/auction_list.html', context)


# ============ Bidding Room Views ============

@login_required(login_url='otp_login')
def bidding_room(request, auction_id):
    """Display live bidding room for an auction"""
    auction = get_object_or_404(Auction, id=auction_id, status='active', is_active=True)
    
    # Get or create bidding room
    bidding_room, created = BiddingRoom.objects.get_or_create(auction=auction)
    
    # Check if user is seller
    is_seller = request.user == auction.seller
    
    # Get or create anonymous bidder ID
    try:
        anon_bidder = AnonymousBidderId.objects.get(user=request.user, auction=auction)
    except AnonymousBidderId.DoesNotExist:
        anon_bidder = None
    
    # Get recent bid history
    recent_bids = BidAudit.objects.filter(
        auction=auction,
        is_valid=True
    ).select_related('anonymous_id').order_by('-created_at')[:20]
    
    # Get all unique bidders with anonymous IDs
    bidders = AnonymousBidderId.objects.filter(
        auction=auction
    ).select_related('user')
    
    context = {
        'auction': auction,
        'bidding_room': bidding_room,
        'is_seller': is_seller,
        'anon_bidder': anon_bidder,
        'recent_bids': reversed(recent_bids),
        'bidders': bidders,
        'current_highest': bidding_room.highest_bid or auction.starting_price,
    }
    
    return render(request, 'livebidding/bidding_room.html', context)


# ============ Auction Creation Views ============

@login_required(login_url='otp_login')
def create_auction(request):
    """Create a new auction for selling livestock"""
    # Only sellers can create auctions
    if not request.user.is_professional_seller:
        return redirect('become_seller')
    
    if request.method == 'POST':
        return handle_create_auction(request)
    
    # GET request - show form
    livestock_types = LivestockType.objects.filter(is_active=True)
    
    context = {
        'livestock_types': livestock_types,
    }
    
    return render(request, 'livebidding/create_auction.html', context)


def handle_create_auction(request):
    """Handle auction creation form submission"""
    try:
        # Get form data
        product_name = request.POST.get('product_name')
        livestock_type = request.POST.get('livestock_type')
        quantity = request.POST.get('quantity')
        starting_price = request.POST.get('starting_price')
        minimum_bid_increment = request.POST.get('minimum_bid_increment')
        reserve_price = request.POST.get('reserve_price')
        description = request.POST.get('description')
        auction_start = request.POST.get('auction_start')
        auction_end = request.POST.get('auction_end')
        
        # Validate inputs
        errors = []
        
        if not product_name:
            errors.append('Product name is required')
        if not livestock_type:
            errors.append('Livestock type is required')
        if not quantity or int(quantity) <= 0:
            errors.append('Quantity must be greater than 0')
        if not starting_price or Decimal(starting_price) <= 0:
            errors.append('Starting price must be greater than 0')
        if not minimum_bid_increment or Decimal(minimum_bid_increment) <= 0:
            errors.append('Minimum bid increment must be greater than 0')
        
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        
        # Parse dates
        from django.utils.dateparse import parse_datetime
        start_time = parse_datetime(auction_start)
        end_time = parse_datetime(auction_end)
        
        if not start_time or not end_time:
            return JsonResponse({'success': False, 'message': 'Invalid date format'}, status=400)
        
        if end_time <= start_time:
            return JsonResponse({'success': False, 'message': 'End time must be after start time'}, status=400)
        
        # Get livestock type
        try:
            livestock = LivestockType.objects.get(slug=livestock_type)
        except LivestockType.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid livestock type'}, status=400)
        
        # Create product and auction
        with transaction.atomic():
            # Create product
            product = Product.objects.create(
                title=product_name,
                description=description,
                seller=request.user,
                livestock_type=livestock,
                quantity=int(quantity),
                status='pending',
                auction_enabled=True,
            )
            
            # Create auction
            auction = Auction.objects.create(
                product=product,
                seller=request.user,
                starting_price=Decimal(starting_price),
                current_price=Decimal(starting_price),
                minimum_bid_increment=Decimal(minimum_bid_increment),
                reserve_price=Decimal(reserve_price) if reserve_price else None,
                start_time=start_time,
                end_time=end_time,
                status='scheduled',
            )
            
            # Create bidding room
            BiddingRoom.objects.create(
                auction=auction,
                is_active=False,  # Will be activated at start time
            )
            
            # Handle uploaded images
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage = Product.images.through  # Get through model
                from products.models import ProductImage as ProductImageModel
                ProductImageModel.objects.create(
                    product=product,
                    image=image,
                )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Auction created successfully',
                'auction_id': auction.id,
                'auction_url': f'/livebidding/auction/{auction.id}/'
            })
        else:
            return redirect('bidding_room', auction_id=auction.id)
    
    except Exception as e:
        logger.error(f"Error creating auction: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


# ============ API Endpoints ============

@login_required(login_url='otp_login')
def api_get_auction_data(request, auction_id):
    """Get auction data for AJAX requests"""
    try:
        auction = Auction.objects.get(id=auction_id)
        bidding_room = BiddingRoom.objects.get(auction=auction)
        
        return JsonResponse({
            'success': True,
            'auction': {
                'id': auction.id,
                'title': auction.product.title,
                'status': auction.status,
                'starting_price': float(auction.starting_price),
                'current_price': float(bidding_room.highest_bid or auction.starting_price),
                'total_bids': bidding_room.total_bids,
                'unique_bidders': bidding_room.active_bidders.count(),
                'end_time': auction.end_time.isoformat(),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=404)


@login_required(login_url='otp_login')
def api_get_bidders(request, auction_id):
    """Get list of bidders with anonymous IDs (except real names)"""
    try:
        auction = Auction.objects.get(id=auction_id)
        
        bidders = AnonymousBidderId.objects.filter(
            auction=auction
        ).values('anonymous_id', 'distance_km')
        
        return JsonResponse({
            'success': True,
            'bidders': list(bidders)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=404)


@login_required(login_url='otp_login')
def api_get_bid_history(request, auction_id):
    """Get bid history for an auction"""
    try:
        auction = Auction.objects.get(id=auction_id)
        limit = request.GET.get('limit', 20)
        
        bids = BidAudit.objects.filter(
            auction=auction,
            is_valid=True
        ).select_related('anonymous_id').order_by('-created_at')[:int(limit)]
        
        bid_list = [
            {
                'anonymous_id': bid.anonymous_id.anonymous_id if bid.anonymous_id else 'Unknown',
                'amount': float(bid.amount),
                'time': bid.created_at.isoformat(),
                'is_winning': bid.is_winning,
            }
            for bid in reversed(bids)
        ]
        
        return JsonResponse({
            'success': True,
            'bids': bid_list
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=404)


# ============ Auction Winner Views ============

@login_required(login_url='otp_login')
def winner_dashboard(request, auction_id):
    """Dashboard for auction winner"""
    try:
        auction_winner = AuctionWinner.objects.get(auction_id=auction_id)
        
        # Check if user is winner or seller
        if request.user != auction_winner.winner and request.user != auction_winner.seller:
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        
        # Determine what info to show
        is_winner = request.user == auction_winner.winner
        is_seller = request.user == auction_winner.seller
        
        context = {
            'auction_winner': auction_winner,
            'is_winner': is_winner,
            'is_seller': is_seller,
        }
        
        return render(request, 'livebidding/winner_dashboard.html', context)
    
    except AuctionWinner.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Auction not found'}, status=404)


@login_required(login_url='otp_login')
@require_POST
def reveal_contact(request, auction_id):
    """Reveal contact details after auction"""
    try:
        auction_winner = AuctionWinner.objects.get(auction_id=auction_id)
        
        if request.user == auction_winner.winner:
            auction_winner.buyer_contact_revealed = True
        elif request.user == auction_winner.seller:
            auction_winner.seller_contact_revealed = True
        else:
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        
        auction_winner.save()
        
        return JsonResponse({'success': True, 'message': 'Contact revealed'})
    
    except AuctionWinner.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Auction not found'}, status=404)


# ============ User Profile Views ============

@login_required(login_url='otp_login')
def user_bidding_history(request):
    """View user's bidding history"""
    # Get user's bid audits
    bid_audits = BidAudit.objects.filter(
        user=request.user
    ).select_related('auction', 'anonymous_id').order_by('-created_at')
    
    # Get user's bidding stats
    bidding_stats = BiddingStats.objects.get(user=request.user)
    
    context = {
        'bid_audits': bid_audits,
        'bidding_stats': bidding_stats,
    }
    
    return render(request, 'livebidding/bidding_history.html', context)
