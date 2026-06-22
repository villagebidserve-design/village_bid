from django.contrib import admin
from django.utils.html import format_html
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'reviewer',
        'product_link',
        'rating_display',
        'verified_purchase_display',
        'is_approved_display',
        'helpful_count',
        'created_at'
    ]
    list_filter = [
        'rating',
        'is_approved',
        'verified_purchase',
        'created_at',
        'communication_rating',
        'shipping_rating'
    ]
    search_fields = ['product__title', 'reviewer__username', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count', 'unhelpful_count']
    
    fieldsets = (
        ('Review Details', {
            'fields': ('product', 'reviewer', 'seller')
        }),
        ('Ratings', {
            'fields': ('rating', 'communication_rating', 'shipping_rating')
        }),
        ('Content', {
            'fields': ('comment',)
        }),
        ('Verification', {
            'fields': ('verified_purchase', 'is_approved')
        }),
        ('Engagement', {
            'fields': ('helpful_count', 'unhelpful_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews', 'mark_verified']
    
    def product_link(self, obj):
        return format_html(
            '<a href="/admin/products/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.title[:50]
        )
    product_link.short_description = 'Product'
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating
        return format_html(
            '<span title="{}/5">{}</span>',
            obj.rating,
            stars
        )
    rating_display.short_description = 'Rating'
    
    def verified_purchase_display(self, obj):
        if obj.verified_purchase:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: gray;">-</span>')
    verified_purchase_display.short_description = 'Verified Purchase'
    
    def is_approved_display(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green;">✓ Approved</span>')
        return format_html('<span style="color: red;">✗ Pending</span>')
    is_approved_display.short_description = 'Status'
    
    def approve_reviews(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} reviews approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def reject_reviews(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} reviews rejected.')
    reject_reviews.short_description = 'Reject selected reviews'
    
    def mark_verified(self, request, queryset):
        count = queryset.update(verified_purchase=True)
        self.message_user(request, f'{count} reviews marked as verified purchase.')
    mark_verified.short_description = 'Mark as verified purchase'

