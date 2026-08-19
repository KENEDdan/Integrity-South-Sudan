from django.conf import settings
from django.db import models

from apps.core.validators import (
    validate_document_extension, validate_document_size,
    validate_image_extension, validate_image_size,
)


class Partner(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(
        upload_to="partners/logos/", validators=[validate_image_extension, validate_image_size],
    )
    base_address = models.CharField(max_length=255)
    contact_address = models.CharField(max_length=255)
    partnering_on = models.CharField(max_length=255, help_text="e.g. Capacity building, Civic education")
    validity_note = models.CharField(max_length=200, blank=True, help_text="e.g. valid until Dec 2027")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PartnerRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    INFO_REQUESTED = "info_requested", "More Information Requested"
    APPROVED = "approved", "Approved"
    DECLINED = "declined", "Declined"


class PartnerRequest(models.Model):
    organization_name = models.CharField(max_length=200)
    logo = models.ImageField(
        upload_to="partners/requests/", blank=True, null=True,
        validators=[validate_image_extension, validate_image_size],
    )
    address = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=30, blank=True)
    registration_documents = models.FileField(
        upload_to="partners/documents/", blank=True, null=True,
        validators=[validate_document_extension, validate_document_size],
    )
    reason = models.TextField(help_text="Why do you want to partner with us?")
    contract_validity = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=20, choices=PartnerRequestStatus.choices, default=PartnerRequestStatus.PENDING)
    admin_notes = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.organization_name} ({self.get_status_display()})"