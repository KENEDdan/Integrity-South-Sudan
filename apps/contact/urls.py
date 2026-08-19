from django.urls import path
from . import views

app_name = "contact"

urlpatterns = [
    path("", views.public_contact, name="public_contact"),
    path("manage/", views.manage_contact, name="manage_contact"),
    path("newsletter-signup/", views.newsletter_signup, name="newsletter_signup"),
]