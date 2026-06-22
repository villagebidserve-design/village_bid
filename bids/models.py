from django.db import models
from django.conf import settings
from auctions.models import Auction
from django.core.validators import MinValueValidator


class Bid(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('outbid', 'Outbid'),
        ('winning', 'Winning'),
        ('won', 'Won'),
    ]

    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bids'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Bid details
    is_winning = models.BooleanField(default=False)
    was_outbid = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-amount', '-created_at']
        indexes = [
            models.Index(fields=['auction', '-amount']),
            models.Index(fields=['bidder']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.bidder.username} - ₹{self.amount} on {self.auction.product.title}"
    
    def mark_as_outbid(self):
        self.status = 'outbid'
        self.is_winning = False
        self.was_outbid = True
        self.save()
    
    def mark_as_winning(self):
        self.status = 'winning'
        self.is_winning = True
        self.save()
