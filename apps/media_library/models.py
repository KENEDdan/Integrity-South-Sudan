from django.conf import settings
from django.db import models

from apps.core.validators import validate_media_asset_extension, validate_media_asset_size


class ResourceType(models.TextChoices):
    PHOTO = "photo", "Photo"
    VIDEO_LINK = "video_link", "Video Link"
    LOGO = "logo", "Logo"
    TEMPLATE = "template", "Template"
    OTHER = "other", "Other"


class MediaResource(models.Model):
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    file = models.FileField(
        upload_to="media_library/", blank=True, null=True,
        validators=[validate_media_asset_extension, validate_media_asset_size],
    )
    external_url = models.URLField(blank=True, help_text="Use for video links instead of uploading a file.")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated, e.g. logo, green, event")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]