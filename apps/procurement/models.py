from django.conf import settings
from django.db import models


class VendorCategory(models.TextChoices):
    GOODS = "goods", "Goods"
    SERVICES = "services", "Services"
    WORKS = "works", "Works"


class Vendor(models.Model):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=VendorCategory.choices)
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Currency(models.TextChoices):
    USD = "USD", "US Dollar"
    SSP = "SSP", "South Sudanese Pound"


class RequisitionStatus(models.TextChoices):
    PENDING = "pending", "Pending Approval"
    APPROVED = "approved", "Approved"
    DECLINED = "declined", "Declined"
    CONVERTED = "converted", "Converted to Purchase Order"


class Requisition(models.Model):
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requisitions")
    related_project = models.ForeignKey(
        "projects.Project", null=True, blank=True, on_delete=models.SET_NULL, related_name="requisitions",
    )
    items_description = models.TextField(help_text="List the items or services needed.")
    justification = models.TextField()
    estimated_cost = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    status = models.CharField(max_length=20, choices=RequisitionStatus.choices, default=RequisitionStatus.PENDING)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="requisitions_decided",
    )
    decision_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Requisition #{self.pk} — {self.currency} {self.estimated_cost}"


class PurchaseOrderStatus(models.TextChoices):
    ISSUED = "issued", "Issued"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class PurchaseOrder(models.Model):
    requisition = models.OneToOneField(Requisition, on_delete=models.CASCADE, related_name="purchase_order")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="purchase_orders")
    po_number = models.CharField(max_length=30, unique=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices)
    status = models.CharField(max_length=20, choices=PurchaseOrderStatus.choices, default=PurchaseOrderStatus.ISSUED)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"{self.po_number} — {self.vendor.name}"


class Delivery(models.Model):
    purchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name="delivery")
    delivered_date = models.DateField()
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    condition_notes = models.TextField(blank=True)
    is_complete = models.BooleanField(default=True)

    def __str__(self):
        return f"Delivery for {self.purchase_order.po_number}"