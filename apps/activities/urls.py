from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    path("", views.public_list, name="public_list"),
    path("<int:pk>/", views.public_detail, name="public_detail"),

    path("manage/", views.manage_list, name="manage_list"),
    path("manage/add/", views.activity_create, name="activity_create"),
    path("manage/<int:pk>/edit/", views.activity_edit, name="activity_edit"),
    path("manage/<int:pk>/delete/", views.activity_delete, name="activity_delete"),
]