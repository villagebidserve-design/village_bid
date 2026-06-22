from django.db import models
from products.models import Product
from django.utils import timezone
from django.core.validators import MinValueValidator
import json


class Auction(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='auction'
    )

    # Pricing
    starting_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    reserve_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    minimum_bid_increment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500,
        validators=[MinValueValidator(0)]
    )

    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Seller info
    seller = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="seller_auctions"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_active = models.BooleanField(default=True)

    # Winner info
    winner = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_auctions"
    )
    
    # Bid info
    total_bids = models.IntegerField(default=0)
    total_bidders = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['end_time']),
        ]

    def __str__(self):
        return f"Auction: {self.product.title}"
    
    def close_auction(self):
        """Close auction and assign winner"""
        if timezone.now() >= self.end_time and self.is_active:
            highest_bid = self.bids.order_by("-amount").first()

            if highest_bid and (self.reserve_price is None or highest_bid.amount >= self.reserve_price):
                self.winner = highest_bid.bidder
            
            self.is_active = False
            self.status = 'ended'
            self.save()
            
            return True
        return False
    
    def can_bid(self, user):
        """Check if user can place a bid"""
        if not user.is_authenticated:
            return False
        if user == self.seller:
            return False
        if getattr(user, 'is_suspended', False):
            return False
        return self.is_active and timezone.now() < self.end_time
    
    def get_time_remaining(self):
        """Get remaining time in seconds"""
        remaining = (self.end_time - timezone.now()).total_seconds()
        return max(0, remaining)

    def formatted_time_remaining(self):
        """Get human-readable remaining time"""
        remaining = int(self.get_time_remaining())
        if remaining <= 0:
            return "Closed"

        days, remainder = divmod(remaining, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds and not parts:
            parts.append(f"{seconds}s")
        return " ".join(parts)
    
    def is_reserve_met(self):
        """Check if reserve price is met"""
        if self.reserve_price is None:
            return True
        return self.current_price >= self.reserve_price
    
    @property
    def bids_count(self):
        return self.bids.count()
