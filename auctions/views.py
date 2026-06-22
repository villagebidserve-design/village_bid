import re

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Max, Q
from django.utils import timezone
from django.utils.html import escape, mark_safe
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Auction
from bids.models import Bid
from bids.forms import BidForm
from notifications.models import Notification
from payments.models import Payment
from django.db import transaction


@require_http_methods(["GET", "POST"])
def auction_detail(request, pk):
    """Enhanced auction detail view with bidding logic"""
    auction = get_object_or_404(
        Auction.objects.select_related('product', 'seller', 'winner').prefetch_related('bids'),
        pk=pk
    )
    
    # Auto-close auction if time has expired
    if auction.is_active and timezone.now() >= auction.end_time:
        auction.close_auction()

    # Check if user can bid
    can_bid = auction.can_bid(request.user)
    
    # Get bids with pagination
    bids = auction.bids.select_related('bidder').order_by("-amount", "-created_at")
    paginator = Paginator(bids, 10)
    page = request.GET.get("page_bids", 1)
    try:
        bids = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        bids = paginator.page(1)

    form = BidForm() if can_bid else None

    if request.method == "POST" and can_bid:
        form = BidForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                bid = form.save(commit=False)
                minimum_bid = auction.current_price + auction.minimum_bid_increment

                # Validate bid amount
                if bid.amount < minimum_bid:
                    messages.error(
                        request,
                        f"Minimum bid must be ₹{minimum_bid}. Your bid: ₹{bid.amount}"
                    )
                elif not auction.is_active:
                    messages.error(request, "This auction has already closed.")
                else:
                    # Save the bid
                    bid.auction = auction
                    bid.bidder = request.user
                    bid.save()
                    
                    # Update auction
                    auction.current_price = bid.amount
                    auction.total_bids += 1
                    auction.save()
                    
                    # Mark previous bids as outbid
                    previous_bids = auction.bids.exclude(pk=bid.pk).order_by("-amount")
                    if previous_bids.exists():
                        highest_previous = previous_bids.first()
                        if highest_previous:
                            highest_previous.mark_as_outbid()
                            
                            # Notify outbid bidder
                            Notification.objects.create(
                                user=highest_previous.bidder,
                                message=f"You were outbid on {auction.product.title}",
                                is_read=False
                            )

                    # Notify seller
                    Notification.objects.create(
                        user=auction.seller,
                        message=f"New bid (₹{bid.amount}) placed on {auction.product.title}",
                        is_read=False
                    )

                    messages.success(
                        request,
                        f"Bid placed successfully! Your bid: ₹{bid.amount}"
                    )
                    
                    return redirect("auction_detail", pk=auction.id)

    # Check if user is current highest bidder
    user_is_leading = False
    user_bids_count = 0
    if request.user.is_authenticated:
        highest_bid = auction.bids.order_by("-amount").first()
        user_is_leading = highest_bid and highest_bid.bidder == request.user
        user_bids_count = auction.bids.filter(bidder=request.user).count()

    # Get related auctions
    similar_auctions = Auction.objects.filter(
        product__category=auction.product.category,
        is_active=True,
        status='active'
    ).exclude(pk=pk)[:4]

    context = {
        "auction": auction,
        "bids": bids,
        "form": form,
        "can_bid": can_bid,
        "user_is_leading": user_is_leading,
        "user_bids_count": user_bids_count,
        "time_remaining": auction.get_time_remaining(),
        "reserve_met": auction.is_reserve_met(),
        "similar_auctions": similar_auctions,
    }

    return render(request, "auctions/detail.html", context)


@login_required
def won_auctions(request):
    """View user's won auctions with pagination"""
    auctions = Auction.objects.filter(
        winner=request.user,
        status='ended'
    ).select_related('product', 'seller').order_by('-end_time')
    
    # Filter by status
    status = request.GET.get("status")
    if status == "unpaid":
        # Won but not paid
        auctions = auctions.exclude(payment__status='completed')
    elif status == "paid":
        # Won and paid
        auctions = auctions.filter(payment__status='completed')
    
    # Pagination
    paginator = Paginator(auctions, 10)
    page = request.GET.get("page", 1)
    try:
        auctions = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        auctions = paginator.page(1)
    
    context = {
        "auctions": auctions,
        "paginator": paginator,
        "status": status,
    }

    return render(request, "auctions/won_auctions.html", context)


@login_required
def my_active_bids(request):
    """View user's active bids"""
    active_bids = Bid.objects.filter(
        bidder=request.user,
        auction__is_active=True,
        status__in=['active', 'winning']
    ).select_related('auction', 'auction__product').order_by('-auction__end_time')
    
    # Pagination
    paginator = Paginator(active_bids, 10)
    page = request.GET.get("page", 1)
    try:
        bids = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        bids = paginator.page(1)
    
    context = {
        "bids": bids,
        "paginator": paginator,
    }

    return render(request, "auctions/my_bids.html", context)


def highlight_query_text(text, query):
    if not query or not text:
        return text

    text = escape(text)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    highlighted = pattern.sub(
        lambda match: f'<mark style="background: rgba(255, 193, 7, 0.35); padding: 0.1rem 0.2rem; border-radius: 0.2rem;">{match.group(0)}</mark>',
        text,
    )
    return mark_safe(highlighted)


def auction_list(request):
    """List all active auctions with filtering and sorting"""
    auctions = Auction.objects.filter(
        status='active',
        is_active=True
    ).select_related('product', 'seller').prefetch_related('bids').order_by('-end_time')
    
    # Filtering
    category = request.GET.get("category")
    if category:
        auctions = auctions.filter(product__category__slug=category)
    
    location = request.GET.get("location")
    if location:
        auctions = auctions.filter(product__location__icontains=location)

    query = request.GET.get("q")
    if query:
        auctions = auctions.filter(
            Q(product__title__icontains=query)
            | Q(product__description__icontains=query)
            | Q(seller__username__icontains=query)
        )
    
    # Sorting
    sort = request.GET.get("sort", "-end_time")
    valid_sorts = ['title', '-title', 'current_price', '-current_price', 'end_time', '-end_time', 'total_bids']
    if sort in valid_sorts:
        if sort == 'total_bids':
            auctions = auctions.annotate(bid_count=Count('bids')).order_by('-bid_count')
        else:
            auctions = auctions.order_by(sort)
    
    # Pagination
    paginator = Paginator(auctions, 12)
    page = request.GET.get("page", 1)
    try:
        auctions = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        auctions = paginator.page(1)

    # Apply highlight strings for client-side rendering
    for auction in auctions:
        auction.highlighted_title = highlight_query_text(auction.product.title, query)
        auction.highlighted_seller = highlight_query_text(auction.seller.username, query)

    # Keep filter/search params when switching pages
    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_string = f"&{query_params.urlencode()}" if query_params else ""

    context = {
        "auctions": auctions,
        "paginator": paginator,
        "category": category,
        "location": location,
        "sort": sort,
        "q": query,
        "query_string": query_string,
    }

    return render(request, "auctions/list.html", context)
