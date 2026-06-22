from django.urls import path
from .views import my_bids

urlpatterns = [

    path(
        "my-bids/",
        my_bids,
        name="my_bids"
    ),

]