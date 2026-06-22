from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )

    # Review seller separately
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seller_reviews_received',
        blank=True,
        null=True
    )

    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    comment = models.TextField(max_length=2000)
    
    # Additional fields
    communication_rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5
    )
    shipping_rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5
    )
    
    # Verification
    verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    unhelpful_count = models.IntegerField(default=0)
    
    # Status
    is_approved = models.BooleanField(default=True)
    is_seller_response = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seller_responses'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['seller']),
            models.Index(fields=['is_approved']),
        ]
        unique_together = [('product', 'reviewer')]

    def __str__(self):
        return f"{self.reviewer.username} - {self.product.title} ({self.rating}★)"
