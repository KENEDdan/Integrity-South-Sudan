import re
from django.conf import settings
from django.db import models

from apps.core.validators import validate_image_extension, validate_image_size


def youtube_id_from_url(url):
    if not url:
        return ""
    match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else ""


class Achievement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to="achievements/thumbnails/", blank=True, null=True,
        validators=[validate_image_extension, validate_image_size],
    )
    youtube_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(
        default=False, help_text="Pin to the permanent Featured section on the homepage.",
    )
    display_order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers show first among featured items.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="achievements",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def youtube_id(self):
        return youtube_id_from_url(self.youtube_url)

    @property
    def youtube_embed_url(self):
        return f"https://www.youtube.com/embed/{self.youtube_id}" if self.youtube_id else ""

    @property
    def youtube_thumbnail_url(self):
        return f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg" if self.youtube_id else ""


class AchievementMedia(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(
        upload_to="achievements/gallery/", blank=True, null=True,
        validators=[validate_image_extension, validate_image_size],
    )
    youtube_url = models.URLField(blank=True)
    caption = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["id"]

    @property
    def youtube_id(self):
        return youtube_id_from_url(self.youtube_url)

    @property
    def youtube_embed_url(self):
        return f"https://www.youtube.com/embed/{self.youtube_id}" if self.youtube_id else ""

    def __str__(self):
        return self.caption or f"Media for {self.achievement.title}"

        