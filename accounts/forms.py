from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile


class SignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone",
            "role",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email


class SignupOTPForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter OTP sent to your email',
            'autocomplete': 'off',
        })
    )

    def clean_otp_code(self):
        otp_code = self.cleaned_data.get('otp_code', '').strip()
        if not otp_code.isdigit() or len(otp_code) != 6:
            raise forms.ValidationError('Enter a valid 6-digit OTP code')
        return otp_code


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = (
            'avatar', 'state', 'district', 'village', 'pincode',
            'notification_email', 'notification_sms'
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = None
        if 'username' in self.cleaned_data or 'email' in self.cleaned_data:
            # Save user fields separately
            user = getattr(profile, 'user', None)
            if user:
                user.username = self.cleaned_data.get('username', user.username)
                user.email = self.cleaned_data.get('email', user.email)
                if commit:
                    user.save()
        if commit:
            profile.save()
        return profile