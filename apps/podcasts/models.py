import re
from django.conf import settings
from django.db import models

from apps.core.validators import validate_image_extension, validate_image_size


def youtube_id_from_url(url):
    if not url:
        return ""
    match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else ""


class Podcast(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Full description/content of the episode.")
    video_url = models.URLField(help_text="Link from YouTube or any other social media platform.")
    thumbnail = models.ImageField(
        upload_to="podcasts/thumbnails/", blank=True, null=True,
        validators=[validate_image_extension, validate_image_size],
    )
    is_published = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="podcasts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def youtube_id(self):
        return youtube_id_from_url(self.video_url)

    @property
    def is_youtube(self):
        return bool(self.youtube_id)

    @property
    def youtube_embed_url(self):
        return f"https://www.youtube.com/embed/{self.youtube_id}" if self.youtube_id else ""