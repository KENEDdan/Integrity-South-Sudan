from django.urls import path
from . import views

app_name = "podcasts"

urlpatterns = [
    path("", views.public_list, name="public_list"),
    path("<int:pk>/", views.public_detail, name="public_detail"),
    path("manage/", views.manage_list, name="manage_list"),
    path("manage/add/", views.podcast_create, name="podcast_create"),
    path("manage/<int:pk>/edit/", views.podcast_edit, name="podcast_edit"),
]