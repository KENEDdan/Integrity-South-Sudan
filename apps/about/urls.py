from django.urls import path
from . import views

app_name = "about"

urlpatterns = [
    path("", views.public_about, name="public_about"),
    path("manage/", views.manage_about, name="manage_about"),
]