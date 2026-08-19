from django.contrib import admin
from .models import Vendor, Requisition, PurchaseOrder, Delivery

admin.site.register(Vendor)
admin.site.register(Requisition)
admin.site.register(PurchaseOrder)
admin.site.register(Delivery)