from django.contrib import admin
from django.utils.html import format_html
from .models import Bid


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = [
        'bidder',
        'auction_link',
        'amount_display',
        'status_badge',
        'winning_display',
        'created_at'
    ]
    list_filter = [
        'status',
        'is_winning',
        'was_outbid',
        'created_at',
        'auction__status'
    ]
    search_fields = ['bidder__username', 'auction__product__title', 'amount']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Bid Information', {
            'fields': ('auction', 'bidder', 'amount')
        }),
        ('Status', {
            'fields': ('status', 'is_winning', 'was_outbid')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_winning', 'mark_as_outbid']
    
    def auction_link(self, obj):
        return format_html(
            '<a href="/admin/auctions/auction/{}/change/">{}</a>',
            obj.auction.id,
            obj.auction.product.title[:40]
        )
    auction_link.short_description = 'Auction'
    
    def amount_display(self, obj):
        return format_html(
            '<strong style="color: green;">₹{}</strong>',
            obj.amount
        )
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'active': 'blue',
            'outbid': 'orange',
            'winning': 'green',
            'won': 'darkgreen'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def winning_display(self, obj):
        if obj.is_winning:
            return format_html('<span style="color: green; font-weight: bold;">🏆 Winning</span>')
        return '-'
    winning_display.short_description = 'Winning'
    
    def mark_as_winning(self, request, queryset):
        count = 0
        for bid in queryset:
            bid.mark_as_winning()
            count += 1
        self.message_user(request, f'{count} bids marked as winning.')
    mark_as_winning.short_description = 'Mark as winning'
    
    def mark_as_outbid(self, request, queryset):
        count = 0
        for bid in queryset:
            bid.mark_as_outbid()
            count += 1
        self.message_user(request, f'{count} bids marked as outbid.')
    mark_as_outbid.short_description = 'Mark as outbid'
