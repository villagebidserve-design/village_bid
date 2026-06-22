from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, SignupOTPForm, ProfileForm
from .models import Profile

def signup_view(request):
    otp_sent = False
    email = None
    otp_form = None
    if request.method == "POST":
        if "send_otp" in request.POST:
            form = SignupForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                from livebidding.services import OTPService
                OTPService.send_otp(email)
                otp_sent = True
                otp_form = SignupOTPForm()
            else:
                otp_form = SignupOTPForm()
        elif "verify_otp" in request.POST:
            form = SignupForm(request.POST)
            otp_form = SignupOTPForm(request.POST)
            email = request.POST.get("email")
            from livebidding.services import OTPService
            if form.is_valid() and otp_form.is_valid() and email:
                verification = OTPService.verify_otp(email, otp_form.cleaned_data["otp_code"], create_user=False)
                if verification["success"]:
                    user = form.save(commit=False)
                    user.email_verified = True
                    user.save()
                    login(request, user)
                    return redirect("home")
                else:
                    messages.error(request, verification["message"])
            otp_sent = True
        else:
            form = SignupForm(request.POST)
            otp_form = SignupOTPForm()
    else:
        form = SignupForm()
        otp_form = SignupOTPForm()

    return render(request, "accounts/signup.html", {"form": form, "otp_sent": otp_sent, "otp_form": otp_form})

class UserLoginView(LoginView):
    template_name = "accounts/login.html"

def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})
