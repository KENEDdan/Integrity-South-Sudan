from django.urls import path
from . import views

app_name = "donations"

urlpatterns = [
    path("", views.donate, name="donate"),
    path("thanks/<int:pk>/", views.donate_thanks, name="donate_thanks"),

    path("manage/", views.donation_list, name="donation_list"),
    path("manage/<int:pk>/confirm/", views.donation_confirm, name="donation_confirm"),
    path("manage/settings/", views.donation_settings, name="donation_settings"),
]