from django.urls import path
from . import views

app_name = "procurement"

urlpatterns = [
    path("requisitions/new/", views.requisition_create, name="requisition_create"),
    path("requisitions/mine/", views.my_requisitions, name="my_requisitions"),
    path("requisitions/", views.requisition_queue, name="requisition_queue"),
    path("requisitions/<int:pk>/decide/", views.requisition_decide, name="requisition_decide"),
    path("requisitions/<int:pk>/issue-po/", views.purchase_order_create, name="purchase_order_create"),

    path("purchase-orders/", views.po_list, name="po_list"),
    path("purchase-orders/<int:pk>/delivery/", views.delivery_record, name="delivery_record"),

    path("vendors/", views.vendor_list, name="vendor_list"),
    path("vendors/add/", views.vendor_add, name="vendor_add"),
]