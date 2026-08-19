from django.urls import path
from . import views

app_name = "field_data"

urlpatterns = [
    path("webhook/kobo/", views.kobo_webhook, name="kobo_webhook"),
    path("", views.submission_list, name="submission_list"),
    path("<int:pk>/", views.submission_detail, name="submission_detail"),
]