from django import forms
from django.core.exceptions import ValidationError
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "category",
            "title",
            "slug",
            "description",
            "price",
            "original_price",
            "quantity",
            "location",
            "state",
            "district",
            "condition",
            "year_of_manufacture",
            "warranty_info",
            "premium_listing",
            "auction_enabled",
            "meta_title",
            "meta_description",
            "meta_keywords",
        ]
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product title',
                'minlength': '5',
                'maxlength': '255',
                'required': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated URL slug'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '6',
                'placeholder': 'Describe your product in detail...',
                'minlength': '20',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price in ₹',
                'min': '0',
                'step': '0.01',
                'required': True
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Original price (optional)',
                'min': '0',
                'step': '0.01'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City/Town',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State (optional)'
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'District (optional)'
            }),
            'condition': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'year_of_manufacture': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Year (optional)'
            }),
            'warranty_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1 year warranty (optional)'
            }),
            'premium_listing': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'auction_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO title (optional)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '2',
                'placeholder': 'SEO description (optional)'
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO keywords (optional)'
            }),
        }


    def clean(self):
        cleaned_data = super().clean()
        
        # Validate title
        title = cleaned_data.get('title', '').strip()
        if len(title) < 5:
            self.add_error('title', 'Title must be at least 5 characters long')
        
        # Validate description
        description = cleaned_data.get('description', '').strip()
        if len(description) < 20:
            self.add_error('description', 'Description must be at least 20 characters')
        
        # Validate price
        price = cleaned_data.get('price')
        if price and price < 0:
            self.add_error('price', 'Price cannot be negative')
        
        # Validate original price
        original_price = cleaned_data.get('original_price')
        if original_price and price and original_price < price:
            self.add_error('original_price', 'Original price should be greater than selling price')
        
        return cleaned_data


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text"]
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the image (for accessibility)'
            }),
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("Image size must be less than 5MB")
        return image


