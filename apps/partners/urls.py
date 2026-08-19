from django.urls import path
from . import views

app_name = "partners"

urlpatterns = [
    path("", views.public_list, name="public_list"),
    path("apply/", views.partner_request_create, name="partner_request_create"),

    path("manage/", views.manage_list, name="manage_list"),
    path("manage/add/", views.partner_create, name="partner_create"),
    path("manage/<int:pk>/edit/", views.partner_edit, name="partner_edit"),

    path("manage/requests/", views.request_queue, name="request_queue"),
    path("manage/requests/<int:pk>/decide/", views.request_decide, name="request_decide"),
]