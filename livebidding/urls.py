"""
URL routing for live bidding system
"""
from django.urls import path
from livebidding import views

app_name = 'livebidding'

urlpatterns = [
    # ============ OTP Authentication ============
    path('api/send-otp/', views.send_otp, name='send_otp'),
    path('api/verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/resend-otp/', views.resend_otp, name='resend_otp'),
    
    # ============ Auction Listing & Bidding ============
    path('auctions/', views.auction_list, name='auction_list'),
    path('auction/<int:auction_id>/', views.bidding_room, name='bidding_room'),
    
    # ============ Auction Creation ============
    path('create-auction/', views.create_auction, name='create_auction'),
    
    # ============ API Endpoints ============
    path('api/auction/<int:auction_id>/data/', views.api_get_auction_data, name='api_get_auction_data'),
    path('api/auction/<int:auction_id>/bidders/', views.api_get_bidders, name='api_get_bidders'),
    path('api/auction/<int:auction_id>/bid-history/', views.api_get_bid_history, name='api_get_bid_history'),
    
    # ============ Winner & Results ============
    path('winner/<int:auction_id>/', views.winner_dashboard, name='winner_dashboard'),
    path('api/winner/<int:auction_id>/reveal-contact/', views.reveal_contact, name='reveal_contact'),
    
    # ============ User History ============
    path('my-bidding-history/', views.user_bidding_history, name='bidding_history'),
]
