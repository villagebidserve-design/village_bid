from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from auctions.models import Auction
from django.core.validators import MinValueValidator
import random
import string

User = get_user_model()


class OTPVerification(models.Model):
    """Track OTP verification for email-based login"""
    
    email = models.EmailField(unique=True)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "OTP Verification"
        verbose_name_plural = "OTP Verifications"
        indexes = [
            models.Index(fields=['email', 'is_verified']),
        ]
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return self.is_verified and not self.is_expired()


class AnonymousBidderId(models.Model):
    """Map real user to anonymous bidder ID (e.g., Bidder A12)"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anonymous_ids')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='anonymous_bidders')
    
    # Anonymous ID format: Bidder A12, Bidder B45, etc.
    prefix = models.CharField(max_length=10, default='Bidder')  # Can be "Bidder", "Seller", etc.
    letter = models.CharField(max_length=1)  # A, B, C...
    number = models.IntegerField()  # 10-99
    anonymous_id = models.CharField(max_length=20, unique=True)  # Full ID like "A12"
    
    distance_km = models.IntegerField(null=True, blank=True)  # Approximate distance in km
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'auction')
        ordering = ['anonymous_id']
        indexes = [
            models.Index(fields=['auction', 'user']),
            models.Index(fields=['anonymous_id']),
        ]
    
    def __str__(self):
        return f"{self.prefix} {self.anonymous_id}"
    
    @classmethod
    def generate_anonymous_id(cls, auction):
        """Generate unique anonymous ID for a bidder in this auction"""
        # Get existing bidders count for this auction
        existing_count = cls.objects.filter(auction=auction).count()
        
        # Use A-Z for letter (26 options), 10-99 for number (90 options)
        letter_index = existing_count % 26
        number = 10 + (existing_count // 26)
        
        letter = chr(65 + letter_index)  # A, B, C...
        anonymous_id = f"{letter}{number:02d}"
        
        return letter, number, anonymous_id


class BiddingRoom(models.Model):
    """Real-time bidding session for an auction"""
    
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='bidding_room')
    
    # Active participants
    active_bidders = models.ManyToManyField(User, related_name='active_bidding_rooms', blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    total_bids = models.IntegerField(default=0)
    unique_bidders = models.IntegerField(default=0)
    
    # Highest bid info
    highest_bid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    highest_bidder = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='highest_bids'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['auction', 'is_active']),
        ]
    
    def __str__(self):
        return f"Bidding Room - {self.auction.product.title}"
    
    def end_room(self):
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()


class BidAudit(models.Model):
    """Audit log for all bids placed - for transparency and fraud detection"""
    
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bid_audits')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bid_audits')
    anonymous_id = models.ForeignKey(AnonymousBidderId, on_delete=models.SET_NULL, null=True)
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    is_winning = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=True)
    
    # Fraud detection
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('outbid', 'Outbid'),
            ('winning', 'Winning'),
            ('won', 'Won'),
            ('rejected', 'Rejected'),
        ],
        default='active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['auction', 'user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Bid: ₹{self.amount} on {self.auction.product.title}"


class AuctionWinner(models.Model):
    """Track auction winners and their details"""
    
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='winner_info')
    
    # Winner info
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_auctions_info')
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auctions_sold'
    )
    
    # Final price
    winning_bid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Contact reveal status
    seller_contact_revealed = models.BooleanField(default=False)
    buyer_contact_revealed = models.BooleanField(default=False)
    
    winner_accepted = models.BooleanField(default=False)
    seller_accepted = models.BooleanField(default=False)
    
    # Timestamps
    auction_ended_at = models.DateTimeField()
    winner_announced_at = models.DateTimeField(auto_now_add=True)
    contact_revealed_at = models.DateTimeField(null=True, blank=True)
    deal_finalized_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-auction_ended_at']
        indexes = [
            models.Index(fields=['winner']),
            models.Index(fields=['seller']),
        ]
    
    def __str__(self):
        return f"Winner: {self.winner.username} - {self.auction.product.title}"
    
    def reveal_contacts(self):
        """Mark both contacts as revealed"""
        self.seller_contact_revealed = True
        self.buyer_contact_revealed = True
        self.contact_revealed_at = timezone.now()
        self.save()


class AntiFraudLog(models.Model):
    """Track suspicious bidding activities"""
    
    FRAUD_TYPES = [
        ('self_bid', 'Self-Bidding Attempt'),
        ('rapid_bids', 'Rapid Consecutive Bids'),
        ('high_amount', 'Unusually High Bid'),
        ('price_jump', 'Large Price Jump'),
        ('duplicate_ip', 'Multiple Accounts Same IP'),
        ('rate_limit', 'Rate Limit Exceeded'),
        ('invalid_bid', 'Invalid Bid Amount'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fraud_logs')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='fraud_logs')
    
    fraud_type = models.CharField(max_length=50, choices=FRAUD_TYPES)
    description = models.TextField()
    
    bid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    
    action_taken = models.CharField(
        max_length=100,
        blank=True,
        help_text="Action taken by system (e.g., bid rejected, user blocked)"
    )
    
    resolved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'severity']),
            models.Index(fields=['auction']),
        ]
    
    def __str__(self):
        return f"{self.get_fraud_type_display()} - {self.user.username} on {self.auction.product.title}"


class LivestockType(models.Model):
    """Available livestock types for auction creation"""
    
    name = models.CharField(max_length=100, unique=True)  # e.g., "Hens", "Goats"
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Icon/image
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome icon class
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Livestock Types"
    
    def __str__(self):
        return self.name


class BiddingStats(models.Model):
    """Statistics for each user's bidding history"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bidding_stats')
    
    total_auctions_participated = models.IntegerField(default=0)
    total_auctions_won = models.IntegerField(default=0)
    total_bids_placed = models.IntegerField(default=0)
    
    total_amount_bid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    total_amount_won = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    fraud_flags = models.IntegerField(default=0)
    blocked = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bidding Stats - {self.user.username}"
