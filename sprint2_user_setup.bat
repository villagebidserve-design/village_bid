@echo off
title VillageBid Sprint 5 Setup

cd /d D:\village_bid_approval

echo Creating accounts\views.py...

(
echo from django.shortcuts import render, redirect
echo from django.contrib.auth import login, logout
echo from django.contrib.auth.views import LoginView
echo from .forms import SignupForm
echo.
echo def signup_view(request^):
echo     if request.method == "POST":
echo         form = SignupForm(request.POST^)
echo         if form.is_valid(^):
echo             user = form.save(^)
echo             login(request, user^)
echo             return redirect("home"^)
echo     else:
echo         form = SignupForm(^)
echo.
echo     return render(request, "accounts/signup.html", {"form": form}^)
echo.
echo class UserLoginView(LoginView^):
echo     template_name = "accounts/login.html"
echo.
echo def logout_view(request^):
echo     logout(request^)
echo     return redirect("home"^)
) > accounts\views.py

echo Creating accounts\urls.py...

(
echo from django.urls import path
echo from .views import signup_view, UserLoginView, logout_view
echo.
echo urlpatterns = [
echo     path("signup/", signup_view, name="signup"^),
echo     path("login/", UserLoginView.as_view(^), name="login"^),
echo     path("logout/", logout_view, name="logout"^),
echo ]
) > accounts\urls.py

echo Creating dashboard\views.py...

(
echo from django.contrib.auth.decorators import login_required
echo from django.shortcuts import render
echo.
echo @login_required
echo def dashboard_home(request^):
echo     return render(
echo         request,
echo         "dashboard/home.html",
echo         {"user": request.user}
echo     )
) > dashboard\views.py

echo Creating dashboard\urls.py...

(
echo from django.urls import path
echo from .views import dashboard_home
echo.
echo urlpatterns = [
echo     path("", dashboard_home, name="dashboard"^),
echo ]
) > dashboard\urls.py

if not exist templates\accounts mkdir templates\accounts
if not exist templates\dashboard mkdir templates\dashboard

echo Creating login template...

(
echo ^{% extends 'base/base.html' %^}
echo.
echo ^{% block content %^}
echo.
echo ^<div class="row justify-content-center"^>
echo     ^<div class="col-md-5"^>
echo         ^<div class="card shadow"^>
echo             ^<div class="card-body"^>
echo                 ^<h2^>Login^</h2^>
echo                 ^<form method="post"^>
echo                     ^{% csrf_token %^}
echo                     {{ form.as_p }}
echo                     ^<button class="btn btn-success w-100"^>
echo                         Login
echo                     ^</button^>
echo                 ^</form^>
echo             ^</div^>
echo         ^</div^>
echo     ^</div^>
echo ^</div^>
echo.
echo ^{% endblock %^}
) > templates\accounts\login.html

echo Creating dashboard template...

(
echo ^{% extends 'base/base.html' %^}
echo.
echo ^{% block content %^}
echo.
echo ^<h1^>Dashboard^</h1^>
echo.
echo ^<div class="card shadow"^>
echo     ^<div class="card-body"^>
echo         ^<h3^>Welcome {{ user.username }}^</h3^>
echo         ^<p^>Role: {{ user.role }}^</p^>
echo     ^</div^>
echo ^</div^>
echo.
echo ^{% endblock %^}
) > templates\dashboard\home.html

echo.
echo ========================================
echo SPRINT 5 FILES CREATED
echo ========================================
echo.
echo MANUAL STEP:
echo Open config\urls.py and add:
echo.
echo path("accounts/", include("accounts.urls")),
echo path("dashboard/", include("dashboard.urls")),
echo.
echo Also import:
echo from django.urls import path, include
echo.
pause