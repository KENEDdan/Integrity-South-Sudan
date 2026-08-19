import re
from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.validators import validate_image_extension, validate_image_size


class NewsCategory(models.TextChoices):
    JOB_ADVERTISEMENT = "job_advertisement", "Job Advertisement"
    UPDATE = "update", "Update"
    NEWS = "news", "News"
    BREAKING_NEWS = "breaking_news", "Breaking News"
    RECENTLY_CONCLUDED_EVENT = "recently_concluded_event", "Recently Concluded Event"
    UPCOMING_EVENT = "upcoming_event", "Upcoming Event"
    INTERNATIONAL_UPDATE = "international_update", "International Update"


def youtube_id_from_url(url):
    if not url:
        return ""
    match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else ""


class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=NewsCategory.choices)
    brief_description = models.CharField(max_length=300, help_text="Shown on the landing page feed card.")
    body = models.TextField(help_text="Full detail shown on the article page.")

    thumbnail = models.ImageField(
        upload_to="newsfeed/thumbnails/", blank=True, null=True,
        validators=[validate_image_extension, validate_image_size],
    )
    youtube_url = models.URLField(blank=True, help_text="YouTube link, used as the feed card preview if no thumbnail.")

    is_published = models.BooleanField(default=True)
    scheduled_for = models.DateTimeField(
        null=True, blank=True, help_text="If set and in the future, this post stays hidden until then.",
    )
    display_until = models.DateField(
        null=True, blank=True, help_text="Leave blank to keep this post visible indefinitely.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="news_posts",
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

    @property
    def is_scheduled(self):
        return bool(self.scheduled_for and self.scheduled_for > timezone.now())

    @property
    def is_expired(self):
        return bool(self.display_until and self.display_until < timezone.now().date())


class NewsMedia(models.Model):
    """Gallery item — image or YouTube video — attached to a NewsPost's detail page."""
    post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(
        upload_to="newsfeed/gallery/", blank=True, null=True,
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
        return self.caption or f"Media for {self.post.title}"