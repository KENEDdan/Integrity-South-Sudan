from django.urls import path
from . import views

app_name = "leadership"

urlpatterns = [
    path("", views.public_list, name="public_list"),
    path("<int:pk>/", views.public_detail, name="public_detail"),

    path("manage/", views.manage_list, name="manage_list"),
    path("manage/add/", views.leader_create, name="leader_create"),
    path("manage/<int:pk>/edit/", views.leader_edit, name="leader_edit"),
]