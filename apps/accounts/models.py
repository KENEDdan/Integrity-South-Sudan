from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    HR = "hr", "HR Management"
    FINANCE = "finance", "Finance"
    MEDIA = "media", "Media Team"
    PROGRAM_MANAGER = "program_manager", "Program Manager"


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=Role.choices)
    must_change_password = models.BooleanField(
        default=True,
        help_text="Forces password reset on first login for admin-created accounts.",
    )
    created_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_accounts",
    )
    phone_number = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == Role.SUPER_ADMIN

    class Role(models.TextChoices):
           SUPER_ADMIN = "super_admin", "Super Admin"
           HR = "hr", "HR Management"
           FINANCE = "finance", "Finance"
           MEDIA = "media", "Media Team"
           PROGRAM_MANAGER = "program_manager", "Program Manager"