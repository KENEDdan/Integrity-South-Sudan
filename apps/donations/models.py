import secrets
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Currency(models.TextChoices):
    USD = "USD", "US Dollar"
    SSP = "SSP", "South Sudanese Pound"


class DonationFrequency(models.TextChoices):
    ONE_TIME = "one_time", "One-Time"
    MONTHLY = "monthly", "Monthly"


class DonationStatus(models.TextChoices):
    PENDING = "pending", "Pending Confirmation"
    CONFIRMED = "confirmed", "Confirmed"


class DonationSettings(models.Model):
    bank_name = models.CharField(max_length=100, default="Ecobank South Sudan")
    account_name = models.CharField(max_length=150, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    swift_code = models.CharField(max_length=30, blank=True)
    mobile_money_note = models.CharField(max_length=200, blank=True)
    instructions = models.TextField(blank=True, default=(
        "Please transfer your donation to the account below and include your reference code "
        "in the transfer description. Our finance team will confirm receipt."
    ))

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Donation Bank Details"


def generate_reference():
    return "ISS-DON-" + secrets.token_hex(3).upper()


class Donation(models.Model):
    reference_code = models.CharField(max_length=20, unique=True, default=generate_reference)
    donor_name = models.CharField(max_length=150)
    donor_email = models.EmailField()
    donor_phone = models.CharField(max_length=30, blank=True)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("1.00"))],
    )
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    frequency = models.CharField(max_length=20, choices=DonationFrequency.choices, default=DonationFrequency.ONE_TIME)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=DonationStatus.choices, default=DonationStatus.PENDING)
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.donor_name} — {self.currency} {self.amount} ({self.get_status_display()})"