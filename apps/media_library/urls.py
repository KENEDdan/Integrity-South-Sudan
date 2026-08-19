from django.urls import path
from . import views

app_name = "media_library"

urlpatterns = [
    path("", views.resource_list, name="resource_list"),
    path("add/", views.resource_add, name="resource_add"),
]