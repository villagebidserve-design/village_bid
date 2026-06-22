from django.urls import path
from .views import auction_detail, won_auctions, my_active_bids, auction_list

urlpatterns = [
    path("", auction_list, name="auction_list"),
    path("<int:pk>/", auction_detail, name="auction_detail"),
    path("won/", won_auctions, name="won_auctions"),
    path("my-bids/", my_active_bids, name="my_bids"),
]
