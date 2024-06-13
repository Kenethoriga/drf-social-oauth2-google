# Example URL configuration in urls.py
from django.urls import path
from .views import GoogleAuthRedirect

urlpatterns = [
    path("google-signup/", GoogleAuthRedirect.as_view()),
]