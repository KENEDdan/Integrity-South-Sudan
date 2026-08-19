from django.urls import path
from . import views

app_name = "achievements"

urlpatterns = [
    path("", views.public_list, name="public_list"),
    path("<int:pk>/", views.public_detail, name="public_detail"),

    path("manage/", views.manage_list, name="manage_list"),
    path("manage/add/", views.achievement_create, name="achievement_create"),
    path("manage/<int:pk>/edit/", views.achievement_edit, name="achievement_edit"),
    path("manage/<int:pk>/delete/", views.achievement_delete, name="achievement_delete"),
]