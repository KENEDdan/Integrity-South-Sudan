from django.conf import settings
from django.db import models


class AssetType(models.TextChoices):
    VEHICLE = "vehicle", "Vehicle"
    EQUIPMENT = "equipment", "Equipment"


class AssetStatus(models.TextChoices):
    IN_USE = "in_use", "In Use"
    IN_STORAGE = "in_storage", "In Storage"
    MAINTENANCE = "maintenance", "Under Maintenance"
    DISPOSED = "disposed", "Disposed"


class Asset(models.Model):
    name = models.CharField(max_length=150, help_text="e.g. Toyota Land Cruiser, Dell Laptop #3")
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    identifier = models.CharField(max_length=100, blank=True, help_text="Plate number or serial number")
    assigned_to = models.ForeignKey(
        "hr.Staff", null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_assets",
    )
    status = models.CharField(max_length=20, choices=AssetStatus.choices, default=AssetStatus.IN_USE)
    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"


class LogType(models.TextChoices):
    FUEL = "fuel", "Fuel"
    MAINTENANCE = "maintenance", "Maintenance / Repair"
    OTHER = "other", "Other"


class AssetLog(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="logs")
    log_type = models.CharField(max_length=20, choices=LogType.choices)
    date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=[("USD", "USD"), ("SSP", "SSP")], default="USD")
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_log_type_display()} — {self.asset.name} ({self.date})"