from django.urls import path
from . import views

app_name = "donations"

urlpatterns = [
    path("", views.donate, name="donate"),
    path("thanks/<str:reference_code>/", views.donate_thanks, name="donate_thanks"),

    path("manage/", views.donation_list, name="donation_list"),
    path("manage/<int:pk>/confirm/", views.donation_confirm, name="donation_confirm"),
    path("manage/<int:pk>/proof/", views.donation_proof_download, name="donation_proof_download"),
    path("manage/settings/", views.donation_settings, name="donation_settings"),
]