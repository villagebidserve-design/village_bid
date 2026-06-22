from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ['avatar', 'state', 'district', 'village', 'pincode', 'bio', 'company_name', 'business_type']
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = [
        'username',
        'email',
        'role_badge',
        'seller_rating_display',
        'verification_badge_display',
        'is_suspended_display',
        'created_at'
    ]
    list_filter = [
        'role',
        'is_verified',
        'is_professional_seller',
        'is_suspended',
        'email_verified',
        'created_at'
    ]
    search_fields = ['username', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'last_login_at', 'seller_stats']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('username', 'email', 'phone')
        }),
        ('Verification', {
            'fields': ('email_verified', 'phone_verified', 'is_verified', 'verification_badge')
        }),
        ('Role & Status', {
            'fields': ('role', 'is_suspended')
        }),
        ('Seller Information', {
            'fields': ('is_professional_seller', 'seller_rating', 'total_products_sold', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Password', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_verified', 'mark_professional_seller', 'suspend_users', 'unsuspend_users']
    
    def role_badge(self, obj):
        colors = {
            'buyer': 'blue',
            'seller': 'green',
            'admin': 'orange',
            'superadmin': 'red'
        }
        color = colors.get(obj.role, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    def seller_rating_display(self, obj):
        if obj.role == 'seller':
            rating = obj.seller_rating
            stars = '⭐' * int(rating) + ('½' if rating % 1 > 0 else '')
            return format_html('<strong>{}</strong> {}'.format(rating, stars))
        return '-'
    seller_rating_display.short_description = 'Seller Rating'
    
    def verification_badge_display(self, obj):
        if obj.is_verified and obj.verification_badge:
            return format_html('<span style="color: green; font-size: 20px;">✓</span>')
        return '-'
    verification_badge_display.short_description = 'Verified'
    
    def is_suspended_display(self, obj):
        if obj.is_suspended:
            return format_html('<span style="color: red; font-weight: bold;">Suspended</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_suspended_display.short_description = 'Status'
    
    def seller_stats(self, obj):
        if obj.role == 'seller':
            return format_html(
                '<p><strong>Products Sold:</strong> {}<br><strong>Reviews:</strong> {}<br><strong>Rating:</strong> {}/5</p>',
                obj.total_products_sold,
                obj.total_reviews,
                obj.seller_rating
            )
        return 'Not a seller'
    seller_stats.short_description = 'Seller Statistics'
    
    def mark_verified(self, request, queryset):
        count = queryset.update(is_verified=True, verification_badge=True)
        self.message_user(request, f'{count} users marked as verified.')
    mark_verified.short_description = 'Mark as verified'
    
    def mark_professional_seller(self, request, queryset):
        count = queryset.filter(role='seller').update(is_professional_seller=True)
        self.message_user(request, f'{count} sellers marked as professional.')
    mark_professional_seller.short_description = 'Mark sellers as professional'
    
    def suspend_users(self, request, queryset):
        count = queryset.update(is_suspended=True)
        self.message_user(request, f'{count} users suspended.')
    suspend_users.short_description = 'Suspend selected users'
    
    def unsuspend_users(self, request, queryset):
        count = queryset.update(is_suspended=False)
        self.message_user(request, f'{count} users unsuspended.')
    unsuspend_users.short_description = 'Unsuspend selected users'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'state', 'district', 'village']
    search_fields = ['user__username', 'state', 'district', 'village']
    readonly_fields = ['created_at', 'updated_at']

