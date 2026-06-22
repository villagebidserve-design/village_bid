from django.urls import path
from .views import (
    add_favorite,
    my_favorites
)

urlpatterns = [

    path(
        "add/<int:product_id>/",
        add_favorite,
        name="add_favorite"
    ),

    path(
        "",
        my_favorites,
        name="my_favorites"
    ),

]