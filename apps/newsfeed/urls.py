from django.urls import path
from . import views

app_name = "newsfeed"

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("news/<int:pk>/", views.post_detail, name="post_detail"),

    path("newsfeed/manage/", views.manage_list, name="manage_list"),
    path("newsfeed/manage/add/", views.post_create, name="post_create"),
    path("newsfeed/manage/<int:pk>/edit/", views.post_edit, name="post_edit"),
    path("newsfeed/manage/<int:pk>/delete/", views.post_delete, name="post_delete"),
    path("newsfeed/manage/calendar/", views.content_calendar, name="content_calendar"),
]