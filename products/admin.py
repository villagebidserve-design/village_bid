from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = [
        'title_with_status',
        'seller',
        'category',
        'price_display',
        'condition',
        'status_badge',
        'views',
        'premium_badge',
        'created_at'
    ]
    list_filter = [
        'status',
        'is_active',
        'premium_listing',
        'auction_enabled',
        'condition',
        'category',
        'created_at',
        'approved'
    ]
    search_fields = ['title', 'description', 'seller__username']
    readonly_fields = ['views', 'likes', 'created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'original_price', 'quantity')
        }),
        ('Location', {
            'fields': ('location', 'state', 'district')
        }),
        ('Product Details', {
            'fields': ('condition', 'year_of_manufacture', 'warranty_info')
        }),
        ('Status & Features', {
            'fields': ('status', 'approved', 'premium_listing', 'auction_enabled', 'is_active', 'is_featured')
        }),
        ('Engagement', {
            'fields': ('views', 'likes')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_products', 'reject_products', 'make_premium', 'remove_premium']
    
    def title_with_status(self, obj):
        status_icons = {
            'approved': '✅',
            'pending': '⏳',
            'rejected': '❌',
            'sold': '🎯',
            'inactive': '🔒',
            'draft': '📝'
        }
        icon = status_icons.get(obj.status, '')
        return f"{icon} {obj.title[:50]}"
    title_with_status.short_description = 'Product'
    
    def status_badge(self, obj):
        colors = {
            'approved': 'green',
            'pending': 'orange',
            'rejected': 'red',
            'sold': 'blue',
            'inactive': 'gray',
            'draft': 'silver'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def price_display(self, obj):
        discount = obj.get_discount_percentage()
        if discount > 0:
            return format_html(
                '<strong>₹{}</strong> <span style="color: red;">-{}%</span>',
                obj.price,
                discount
            )
        return format_html('<strong>₹{}</strong>', obj.price)
    price_display.short_description = 'Price'
    
    def premium_badge(self, obj):
        if obj.premium_listing:
            return format_html(
                '<span style="background-color: gold; color: black; padding: 3px 10px; border-radius: 3px;">⭐ Premium</span>'
            )
        return '-'
    premium_badge.short_description = 'Premium'
    
    def approve_products(self, request, queryset):
        count = queryset.update(status='approved', approved=True)
        self.message_user(request, f'{count} products approved.')
    approve_products.short_description = 'Approve selected products'
    
    def reject_products(self, request, queryset):
        count = queryset.update(status='rejected', approved=False)
        self.message_user(request, f'{count} products rejected.')
    reject_products.short_description = 'Reject selected products'
    
    def make_premium(self, request, queryset):
        count = queryset.update(premium_listing=True)
        self.message_user(request, f'{count} products marked as premium.')
    make_premium.short_description = 'Mark as premium'
    
    def remove_premium(self, request, queryset):
        count = queryset.update(premium_listing=False)
        self.message_user(request, f'{count} products removed from premium.')
    remove_premium.short_description = 'Remove from premium'

    def save_model(self, request, obj, form, change):
        if not change or not obj.seller_id:
            obj.seller = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__title']
    readonly_fields = ['image_preview', 'created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" />',
                obj.image.url
            )
        return 'No image'
    image_preview.short_description = 'Preview'
