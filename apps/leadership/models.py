from django.conf import settings
from django.db import models

from apps.core.validators import validate_image_extension, validate_image_size


class Leader(models.Model):
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    qualifications = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    biography = models.TextField()
    photo = models.ImageField(
        upload_to="leadership/", blank=True, null=True,
        validators=[validate_image_extension, validate_image_size],
    )
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.name} — {self.title}"