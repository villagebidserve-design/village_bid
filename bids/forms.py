from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from .models import Bid


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your bid amount',
                'min': '0',
                'step': '0.01',
                'required': True,
                'inputmode': 'decimal',
            })
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if amount is None:
            raise ValidationError("Bid amount is required")
        
        if amount <= 0:
            raise ValidationError("Bid amount must be greater than 0")
        
        # Check if amount has at most 2 decimal places
        if amount % Decimal('0.01') != 0:
            raise ValidationError("Bid amount can have at most 2 decimal places")
        
        return amount
