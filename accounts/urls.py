from django.urls import path
from .views import signup_view, UserLoginView, logout_view, profile_view, edit_profile

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
]
