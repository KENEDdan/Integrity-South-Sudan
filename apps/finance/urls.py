from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/mine/", views.my_requests, name="my_requests"),
    path("requests/<int:pk>/additional-info/", views.submit_additional_info, name="submit_additional_info"),

    path("queue/", views.finance_request_queue, name="request_queue"),
    path("queue/<int:pk>/forward/", views.forward_request, name="forward_request"),
    path("queue/<int:pk>/disburse/", views.confirm_disbursement, name="confirm_disbursement"),
    path("queue/<int:pk>/acknowledge-decline/", views.acknowledge_decline, name="acknowledge_decline"),

    path("super-admin-queue/", views.super_admin_queue, name="super_admin_queue"),
    path("super-admin-queue/<int:pk>/decide/", views.super_admin_decide, name="super_admin_decide"),

    path("transactions/new/", views.transaction_create, name="transaction_create"),
    path("balances/", views.dashboard_balances, name="dashboard_balances"),
]