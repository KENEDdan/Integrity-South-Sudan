from django.conf import settings
from django.db import models


class AuditLogEntry(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name="audit_entries",
    )
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Audit log entries"

    def __str__(self):
        return f"{self.actor}: {self.action}"