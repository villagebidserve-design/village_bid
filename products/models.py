from django.db import models
from django.conf import settings
from categories.models import Category
from django.core.validators import MinValueValidator


class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),
        ('inactive', 'Inactive'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('used', 'Used'),
    ]
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    
    # Basic information
    title = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField()
    
    # Pricing and inventory
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    original_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    
    # Location and logistics
    location = models.CharField(max_length=255)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    
    # Product details
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='used'
    )
    year_of_manufacture = models.IntegerField(null=True, blank=True)
    warranty_info = models.CharField(max_length=255, blank=True)
    
    # Status and features
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    premium_listing = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    auction_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Engagement metrics
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-premium_listing", "-is_featured", "-created_at"]
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['seller']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]
        verbose_name_plural = "Products"

    def __str__(self):
        status_badge = "Premium" if self.premium_listing else "Standard"
        return f"{self.title} ({status_badge})"
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            discount = ((self.original_price - self.price) / self.original_price) * 100
            return int(discount)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/%Y/%m/%d/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"{self.product.title} image"
    


