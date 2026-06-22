from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, Order


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id_display',
        'buyer_link',
        'seller_link',
        'amount_display',
        'status_badge',
        'payment_method',
        'created_at'
    ]
    list_filter = [
        'status',
        'payment_method',
        'created_at',
        'completed_at'
    ]
    search_fields = ['transaction_id', 'buyer__username', 'seller__username', 'razorpay_payment_id']
    readonly_fields = [
        'transaction_id',
        'razorpay_order_id',
        'razorpay_payment_id',
        'created_at',
        'completed_at',
        'failed_at',
        'refunded_at',
        'updated_at',
        'payment_summary'
    ]
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'buyer', 'seller')
        }),
        ('Order Details', {
            'fields': ('auction', 'product', 'amount', 'tax', 'commission', 'total_amount')
        }),
        ('Status', {
            'fields': ('status', 'payment_method')
        }),
        ('Payment Gateway', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'failed_at', 'refunded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'refund_payment']
    
    def transaction_id_display(self, obj):
        return format_html(
            '<code style="background-color: #f0f0f0; padding: 2px 5px;">{}</code>',
            obj.transaction_id[:20] + '...' if obj.transaction_id and len(obj.transaction_id) > 20 else obj.transaction_id or 'N/A'
        )
    transaction_id_display.short_description = 'Transaction ID'
    
    def buyer_link(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.buyer.id,
            obj.buyer.username
        )
    buyer_link.short_description = 'Buyer'
    
    def seller_link(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.seller.id,
            obj.seller.username
        )
    seller_link.short_description = 'Seller'
    
    def amount_display(self, obj):
        return format_html(
            '<strong style="color: green;">₹{:.2f}</strong>',
            obj.total_amount
        )
    amount_display.short_description = 'Total Amount'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'gray',
            'cancelled': 'darkred'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_summary(self, obj):
        return format_html(
            '<p><strong>Subtotal:</strong> ₹{:.2f}<br>'
            '<strong>Tax:</strong> ₹{:.2f}<br>'
            '<strong>Commission:</strong> ₹{:.2f}<br>'
            '<strong>Total:</strong> ₹{:.2f}</p>',
            obj.amount,
            obj.tax,
            obj.commission,
            obj.total_amount
        )
    payment_summary.short_description = 'Payment Summary'
    
    def mark_as_completed(self, request, queryset):
        count = 0
        for payment in queryset:
            payment.mark_as_completed()
            count += 1
        self.message_user(request, f'{count} payments marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_failed(self, request, queryset):
        count = 0
        for payment in queryset:
            payment.mark_as_failed()
            count += 1
        self.message_user(request, f'{count} payments marked as failed.')
    mark_as_failed.short_description = 'Mark as failed'
    
    def refund_payment(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status == 'completed':
                payment.refund()
                count += 1
        self.message_user(request, f'{count} payments refunded.')
    refund_payment.short_description = 'Refund selected payments'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id',
        'buyer_link',
        'seller_link',
        'amount_display',
        'status_badge',
        'tracking_display',
        'created_at'
    ]
    list_filter = [
        'status',
        'created_at',
        'delivered_at',
        'shipped_at'
    ]
    search_fields = ['payment__transaction_id', 'payment__buyer__username', 'tracking_number']
    readonly_fields = ['created_at', 'updated_at', 'order_summary']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('payment',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'tracking_number')
        }),
        ('Timestamps', {
            'fields': ('confirmed_at', 'shipped_at', 'delivered_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_id(self, obj):
        return f'#{obj.id}'
    order_id.short_description = 'Order ID'
    
    def buyer_link(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.payment.buyer.id,
            obj.payment.buyer.username
        )
    buyer_link.short_description = 'Buyer'
    
    def seller_link(self, obj):
        return format_html(
            '<a href="/admin/accounts/user/{}/change/">{}</a>',
            obj.payment.seller.id,
            obj.payment.seller.username
        )
    seller_link.short_description = 'Seller'
    
    def amount_display(self, obj):
        return format_html(
            '<strong style="color: green;">₹{:.2f}</strong>',
            obj.payment.total_amount
        )
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'shipped': 'lightblue',
            'delivered': 'green',
            'cancelled': 'red',
            'returned': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def tracking_display(self, obj):
        if obj.tracking_number:
            return format_html('<code>{}</code>', obj.tracking_number)
        return '-'
    tracking_display.short_description = 'Tracking'
    
    def order_summary(self, obj):
        return format_html(
            '<p><strong>Amount:</strong> ₹{:.2f}<br>'
            '<strong>Status:</strong> {}<br>'
            '<strong>Tracking:</strong> {}</p>',
            obj.payment.total_amount,
            obj.get_status_display(),
            obj.tracking_number or 'Not available'
        )
    order_summary.short_description = 'Order Summary'

