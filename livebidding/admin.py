from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from livebidding.models import (
    OTPVerification, AnonymousBidderId, BiddingRoom, BidAudit,
    AuctionWinner, AntiFraudLog, LivestockType, BiddingStats
)


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_verified_display', 'attempts', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Email Information', {
            'fields': ('email',)
        }),
        ('OTP Details', {
            'fields': ('otp_code', 'is_verified', 'attempts', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_verified_display(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Not Verified</span>'
        )
    is_verified_display.short_description = 'Verification Status'


@admin.register(AnonymousBidderId)
class AnonymousBidderIdAdmin(admin.ModelAdmin):
    list_display = ['anonymous_id', 'user_username', 'auction_product', 'distance_km', 'created_at']
    list_filter = ['created_at', 'distance_km']
    search_fields = ['anonymous_id', 'user__username', 'auction__product__title']
    readonly_fields = ['anonymous_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'auction')
        }),
        ('Anonymous ID', {
            'fields': ('prefix', 'letter', 'number', 'anonymous_id')
        }),
        ('Location', {
            'fields': ('distance_km',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Bidder'
    
    def auction_product(self, obj):
        return obj.auction.product.title
    auction_product.short_description = 'Product'


@admin.register(BiddingRoom)
class BiddingRoomAdmin(admin.ModelAdmin):
    list_display = ['auction_product', 'is_active_display', 'total_bids', 'unique_bidders', 'highest_bid', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['auction__product__title']
    readonly_fields = ['total_bids', 'unique_bidders', 'created_at', 'updated_at', 'ended_at']
    
    fieldsets = (
        ('Auction Information', {
            'fields': ('auction', 'is_active')
        }),
        ('Bidding Statistics', {
            'fields': ('total_bids', 'unique_bidders', 'active_bidders')
        }),
        ('Highest Bid', {
            'fields': ('highest_bid', 'highest_bidder')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'ended_at'),
            'classes': ('collapse',)
        }),
    )
    
    def auction_product(self, obj):
        return obj.auction.product.title
    auction_product.short_description = 'Product'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">● Active</span>'
            )
        return format_html(
            '<span style="color: red;">● Ended</span>'
        )
    is_active_display.short_description = 'Status'


@admin.register(BidAudit)
class BidAuditAdmin(admin.ModelAdmin):
    list_display = ['auction_product', 'user_username', 'anonymous_id', 'amount_display', 'status_badge', 'created_at']
    list_filter = ['status', 'is_valid', 'created_at']
    search_fields = ['user__username', 'auction__product__title', 'anonymous_id__anonymous_id']
    readonly_fields = ['created_at', 'ip_address', 'user_agent', 'device_fingerprint']
    
    fieldsets = (
        ('Bid Information', {
            'fields': ('auction', 'user', 'anonymous_id', 'amount')
        }),
        ('Status', {
            'fields': ('status', 'is_valid', 'is_winning')
        }),
        ('Fraud Detection', {
            'fields': ('ip_address', 'user_agent', 'device_fingerprint'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def auction_product(self, obj):
        return obj.auction.product.title
    auction_product.short_description = 'Product'
    
    def user_username(self, obj):
        return obj.user.username if obj.user else 'N/A'
    user_username.short_description = 'Bidder'
    
    def anonymous_id(self, obj):
        return obj.anonymous_id.anonymous_id if obj.anonymous_id else 'N/A'
    anonymous_id.short_description = 'Anonymous ID'
    
    def amount_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">₹{}</span>',
            obj.amount
        )
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'active': 'blue',
            'outbid': 'orange',
            'winning': 'green',
            'won': 'darkgreen',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(AuctionWinner)
class AuctionWinnerAdmin(admin.ModelAdmin):
    list_display = ['auction_product', 'winner_name', 'winning_bid_amount', 'deal_status', 'winner_announced_at']
    list_filter = ['winner_accepted', 'seller_accepted', 'winner_announced_at']
    search_fields = ['winner__username', 'seller__username', 'auction__product__title']
    readonly_fields = ['winner_announced_at', 'contact_revealed_at']
    
    fieldsets = (
        ('Auction & Participants', {
            'fields': ('auction', 'winner', 'seller')
        }),
        ('Price', {
            'fields': ('winning_bid_amount',)
        }),
        ('Contact Reveal', {
            'fields': ('seller_contact_revealed', 'buyer_contact_revealed', 'contact_revealed_at')
        }),
        ('Deal Status', {
            'fields': ('winner_accepted', 'seller_accepted', 'deal_finalized_at')
        }),
        ('Timestamps', {
            'fields': ('auction_ended_at', 'winner_announced_at'),
            'classes': ('collapse',)
        }),
    )
    
    def auction_product(self, obj):
        return obj.auction.product.title
    auction_product.short_description = 'Product'
    
    def winner_name(self, obj):
        return obj.winner.username
    winner_name.short_description = 'Winner'
    
    def deal_status(self, obj):
        if obj.deal_finalized_at:
            return format_html(
                '<span style="color: darkgreen; font-weight: bold;">✓ Finalized</span>'
            )
        elif obj.winner_accepted and obj.seller_accepted:
            return format_html(
                '<span style="color: green;">Both Accepted</span>'
            )
        return format_html(
            '<span style="color: orange;">Pending</span>'
        )
    deal_status.short_description = 'Deal Status'


@admin.register(AntiFraudLog)
class AntiFraudLogAdmin(admin.ModelAdmin):
    list_display = ['fraud_type_display', 'user_username', 'auction_product', 'severity_badge', 'resolved', 'created_at']
    list_filter = ['fraud_type', 'severity', 'resolved', 'created_at']
    search_fields = ['user__username', 'auction__product__title', 'description']
    readonly_fields = ['created_at', 'ip_address']
    
    fieldsets = (
        ('Fraud Information', {
            'fields': ('user', 'auction', 'fraud_type', 'description')
        }),
        ('Bid Information', {
            'fields': ('bid_amount', 'ip_address')
        }),
        ('Severity & Action', {
            'fields': ('severity', 'action_taken', 'resolved', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def fraud_type_display(self, obj):
        return obj.get_fraud_type_display()
    fraud_type_display.short_description = 'Fraud Type'
    
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'User'
    
    def auction_product(self, obj):
        return obj.auction.product.title
    auction_product.short_description = 'Product'
    
    def severity_badge(self, obj):
        colors = {
            'low': 'blue',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred',
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'


@admin.register(LivestockType)
class LivestockTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display', {
            'fields': ('icon', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BiddingStats)
class BiddingStatsAdmin(admin.ModelAdmin):
    list_display = ['user_username', 'total_auctions_won', 'total_bids_placed', 'total_amount_won', 'blocked', 'updated_at']
    list_filter = ['blocked', 'total_auctions_won', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['updated_at', 'user']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Participation Statistics', {
            'fields': ('total_auctions_participated', 'total_auctions_won', 'total_bids_placed')
        }),
        ('Financial Statistics', {
            'fields': ('total_amount_bid', 'total_amount_won')
        }),
        ('Fraud & Status', {
            'fields': ('fraud_flags', 'blocked')
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'User'
