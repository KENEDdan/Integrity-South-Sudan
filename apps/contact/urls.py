from django.urls import path
from . import views

app_name = "contact"

urlpatterns = [
    path("", views.public_contact, name="public_contact"),
    path("manage/", views.manage_contact, name="manage_contact"),
]