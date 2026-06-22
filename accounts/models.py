from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.utils import timezone


class User(AbstractUser):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

    ROLE_CHOICES = [
        (BUYER, "Buyer"),
        (SELLER, "Seller"),
        (ADMIN, "Admin"),
        (SUPERADMIN, "Super Admin"),
    ]

    # Contact information
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True
    )

    # User role and verification
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=BUYER
    )

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Seller specific fields
    is_professional_seller = models.BooleanField(default=False)
    seller_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_products_sold = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    
    # Account status
    is_suspended = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_badge = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_professional_seller']),
        ]

    def __str__(self):
        return self.username
    
    def get_seller_rating(self):
        """Get average seller rating from reviews"""
        return self.seller_rating
    
    def is_seller(self):
        return self.role == self.SELLER
    
    def is_buyer(self):
        return self.role == self.BUYER
    
    
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Profile information
    avatar = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    # Location details
    state = models.CharField(
        max_length=100,
        blank=True
    )

    district = models.CharField(
        max_length=100,
        blank=True
    )

    village = models.CharField(
        max_length=100,
        blank=True
    )
    
    pincode = models.CharField(
        max_length=10,
        blank=True
    )

    # Bio and description
    bio = models.TextField(blank=True, max_length=500)
    company_name = models.CharField(max_length=200, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    
    # Social links
    website = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Preferences
    notification_email = models.BooleanField(default=True)
    notification_sms = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"
    