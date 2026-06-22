from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg, Count, F
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Product, ProductImage
from .forms import ProductForm
from reviews.forms import ReviewForm
from reviews.models import Review
from favorites.models import Favorite
from django.http import JsonResponse
from auctions.models import Auction
from livebidding.models import BiddingRoom
from datetime import timedelta
from decimal import Decimal


def product_list(request):
    """Advanced product listing with filtering, search, and pagination"""
    products = Product.objects.filter(is_active=True, approved=True, status='approved').select_related(
        'seller', 'category'
    ).prefetch_related('images', 'reviews').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )

    # Search functionality
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Filtering
    location = request.GET.get("location", "").strip()
    if location:
        products = products.filter(location__icontains=location)

    category = request.GET.get("category")
    if category:
        products = products.filter(category__slug=category)

    # Price range filter
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Premium filter
    premium = request.GET.get("premium")
    if premium == "1":
        products = products.filter(premium_listing=True)

    # Condition filter
    condition = request.GET.get("condition")
    if condition:
        products = products.filter(condition=condition)

    # Auction only filter
    auction_only = request.GET.get("auction")
    if auction_only == "1":
        products = products.filter(auction_enabled=True)

    # Sorting
    sort = request.GET.get("sort", "-created_at")
    valid_sorts = [
        'title', '-title', 'price', '-price',
        'created_at', '-created_at', 'avg_rating'
    ]
    if sort in valid_sorts:
        products = products.order_by(sort)

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get("page", 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "query": query,
        "location": location,
        "category": category,
        "min_price": min_price,
        "max_price": max_price,
        "premium": premium,
        "condition": condition,
        "auction_only": auction_only,
        "sort": sort,
        "paginator": paginator,
    }

    return render(request, "products/list.html", context)


def product_detail(request, pk):
    """Enhanced product detail view"""
    product = get_object_or_404(
        Product.objects.select_related('seller', 'category').prefetch_related('images', 'reviews'),
        pk=pk,
        approved=True,
        is_active=True
    )
    
    # Increment view count
    product.increment_views()
    
    reviews = product.reviews.filter(is_approved=True).select_related('reviewer')
    review_form = ReviewForm()

    # Seller stats
    seller_reviews = Review.objects.filter(
        product__seller=product.seller,
        is_approved=True
    ).aggregate(
        avg_rating=Avg('rating'),
        count=Count('id')
    )
    
    # Check if user favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user,
            product=product
        ).exists()
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        approved=True
    ).exclude(pk=pk)[:4]

    auction = None
    try:
        auction = product.auction
    except Exception:
        auction = None

    context = {
        "product": product,
        "reviews": reviews,
        "review_form": review_form,
        "seller_rating": seller_reviews['avg_rating'] or 0,
        "seller_review_count": seller_reviews['count'] or 0,
        "is_favorited": is_favorited,
        "related_products": related_products,
        "auction": auction,
    }

    return render(request, "products/detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def create_product(request):
    """Create new product listing"""
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            # Mark product as published/live when seller publishes
            product.status = 'approved'
            product.approved = True
            product.published_at = timezone.now()
            product.save()

            # Handle image uploads
            images = request.FILES.getlist("images")
            for index, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=(index == 0)
                )

            messages.success(
                request,
                "Your listing is live. After approval steps (if any) we will notify buyers."
            )

            # If this product should start as an auction, create and start it immediately
            if product.auction_enabled:
                try:
                    start_time = timezone.now()
                    end_time = start_time + timedelta(hours=24)
                    auction = Auction.objects.create(
                        product=product,
                        seller=request.user,
                        starting_price=Decimal(product.price),
                        current_price=Decimal(product.price),
                        minimum_bid_increment=Decimal('500.00'),
                        reserve_price=None,
                        start_time=start_time,
                        end_time=end_time,
                        status='active',
                        is_active=True,
                    )
                    # Ensure a live bidding room exists for real-time bidding UI
                    try:
                        BiddingRoom.objects.get_or_create(auction=auction, defaults={
                            'is_active': True,
                            'total_bids': 0,
                            'unique_bidders': 0,
                        })
                    except Exception:
                        # Non-fatal: log later if needed; proceed with redirect
                        pass
                    messages.success(request, "Auction created and started.")
                    return redirect("auction_detail", pk=auction.id)
                except Exception:
                    messages.warning(request, "Listing published but auction setup failed. See product page.")
                    return redirect("product_detail", pk=product.pk)

            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(request, "products/create.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def edit_product(request, pk):
    """Edit existing product"""
    product = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.status = 'pending'
            product.approved = False
            product.save()

            # Handle new images
            images = request.FILES.getlist("images")
            for image in images:
                ProductImage.objects.create(product=product, image=image)

            messages.success(
                request,
                "Product updated and sent for re-approval."
            )
            return redirect("my_listings")
    else:
        form = ProductForm(instance=product)

    context = {
        "form": form,
        "product": product,
        "images": product.images.all(),
    }

    return render(request, "products/edit_product.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def delete_product(request, pk):
    """Delete product"""
    product = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("my_listings")

    return render(request, "products/delete_confirm.html", {"product": product})


@login_required
def my_listings(request):
    """View seller's own listings"""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')

    # Filter by status
    status = request.GET.get("status")
    if status in ['draft', 'pending', 'approved', 'rejected', 'sold', 'inactive']:
        products = products.filter(status=status)

    # Pagination
    paginator = Paginator(products, 10)
    page = request.GET.get("page", 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "status": status,
        "paginator": paginator,
    }

    return render(request, "products/my_listings.html", context)