from django.shortcuts import (
    redirect,
    render
)

from django.contrib.auth.decorators import login_required

from .models import Favorite
from products.models import Product


@login_required
def add_favorite(request, product_id):

    product = Product.objects.get(
        id=product_id
    )

    Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(
        "product_detail",
        pk=product.id
    )


@login_required
def my_favorites(request):

    favorites = Favorite.objects.filter(
        user=request.user
    )

    return render(
        request,
        "favorites/my_favorites.html",
        {
            "favorites": favorites
        }
    )