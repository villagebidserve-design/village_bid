from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from .models import Auction
from bids.models import Bid


class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ['bidder', 'amount', 'status', 'created_at']
    fields = ['bidder', 'amount', 'status', 'created_at']
    can_delete = False


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    inlines = [BidInline]
    list_display = [
        'product_title',
        'status_badge',
        'seller',
        'current_price_display',
        'total_bids',
        'time_remaining_display',
        'winner_display',
        'end_time'
    ]
    list_filter = [
        'status',
        'is_active',
        'start_time',
        'end_time',
        ('current_price', admin.NumericRangeFilter) if hasattr(admin, 'NumericRangeFilter') else 'status',
    ]
    search_fields = ['product__title', 'seller__username', 'winner__username']
    readonly_fields = [
        'total_bids',
        'total_bidders',
        'seller',
        'winner',
        'created_at',
        'updated_at',
        'auction_summary'
    ]
    
    fieldsets = (
        ('Auction & Product', {
            'fields': ('product', 'seller', 'status')
        }),
        ('Pricing', {
            'fields': ('starting_price', 'current_price', 'reserve_price', 'minimum_bid_increment')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Status', {
            'fields': ('is_active', 'winner')
        }),
        ('Statistics', {
            'fields': ('total_bids', 'total_bidders', 'auction_summary'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['close_auctions', 'activate_auctions', 'cancel_auctions']
    
    def product_title(self, obj):
        return format_html(
            '<strong><a href="/admin/products/product/{}/change/">{}</a></strong>',
            obj.product.id,
            obj.product.title[:50]
        )
    product_title.short_description = 'Product'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'scheduled': 'blue',
            'active': 'green',
            'ended': 'orange',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def current_price_display(self, obj):
        reserve_met = obj.is_reserve_met()
        color = 'green' if reserve_met else 'red'
        return format_html(
            '<strong style="color: {};">₹{}</strong>',
            color,
            obj.current_price
        )
    current_price_display.short_description = 'Current Price'
    
    def time_remaining_display(self, obj):
        remaining = obj.get_time_remaining()
        if remaining > 0:
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            if hours > 24:
                days = hours // 24
                return format_html(
                    '<span style="color: green;">{} days</span>',
                    days
                )
            elif hours > 0:
                return format_html(
                    '<span style="color: orange;">{} hours</span>',
                    hours
                )
            else:
                return format_html(
                    '<span style="color: red;">{} minutes</span>',
                    minutes
                )
        return format_html('<span style="color: gray;">Closed</span>')
    time_remaining_display.short_description = 'Time Remaining'
    
    def winner_display(self, obj):
        if obj.winner:
            return format_html(
                '<strong><a href="/admin/accounts/user/{}/change/">{}</a></strong>',
                obj.winner.id,
                obj.winner.username
            )
        return '-'
    winner_display.short_description = 'Winner'
    
    def auction_summary(self, obj):
        return format_html(
            '<p><strong>Starting Price:</strong> ₹{}<br>'
            '<strong>Current Price:</strong> ₹{}<br>'
            '<strong>Reserve Price:</strong> ₹{}<br>'
            '<strong>Total Bids:</strong> {}<br>'
            '<strong>Unique Bidders:</strong> {}<br>'
            '<strong>Reserve Met:</strong> {}</p>',
            obj.starting_price,
            obj.current_price,
            obj.reserve_price or 'Not set',
            obj.total_bids,
            obj.total_bidders,
            '✓ Yes' if obj.is_reserve_met() else '✗ No'
        )
    auction_summary.short_description = 'Auction Summary'
    
    def close_auctions(self, request, queryset):
        count = 0
        for auction in queryset:
            if auction.close_auction():
                count += 1
        self.message_user(request, f'{count} auctions closed.')
    close_auctions.short_description = 'Close selected auctions'
    
    def activate_auctions(self, request, queryset):
        count = queryset.filter(status='scheduled').update(status='active', is_active=True)
        self.message_user(request, f'{count} auctions activated.')
    activate_auctions.short_description = 'Activate selected auctions'
    
    def cancel_auctions(self, request, queryset):
        count = queryset.filter(is_active=True).update(status='cancelled', is_active=False)
        self.message_user(request, f'{count} auctions cancelled.')
    cancel_auctions.short_description = 'Cancel selected auctions'
