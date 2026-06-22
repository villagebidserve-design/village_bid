from django.urls import path

from .views import (
    product_list,
    product_detail,
    create_product,
    my_listings,
    edit_product,
    delete_product,
)

urlpatterns = [

    path(
        "",
        product_list,
        name="product_list"
    ),

    path(
        "create/",
        create_product,
        name="create_product"
    ),

    path(
        "<int:pk>/",
        product_detail,
        name="product_detail"
    ),
    path(
    "my-listings/",
    my_listings,
    name="my_listings"
),
path(
    "edit/<int:pk>/",
    edit_product,
    name="edit_product"
),

path(
    "delete/<int:pk>/",
    delete_product,
    name="delete_product"
),
]