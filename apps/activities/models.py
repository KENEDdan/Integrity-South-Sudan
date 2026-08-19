import re
from django.conf import settings
from django.db import models

from apps.core.validators import validate_image_extension, validate_image_size


def youtube_id_from_url(url):
    if not url:
        return ""
    match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else ""


class ActivityType(models.TextChoices):
    CAPACITY_BUILDING = "capacity_building", "Capacity Building"
    RADIO_PROGRAMS = "radio_programs", "Radio Programs (Integrity Hour)"
    SCHOOL_CLUBS = "school_clubs", "School Clubs"
    COMMUNITY_DIALOGUE = "community_dialogue", "Community Dialogue"
    CIVIC_EDUCATION = "civic_education", "Civic Education"


class Activity(models.Model):
    title = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=30, choices=ActivityType.choices)
    date = models.DateField()
    venue = models.CharField(max_length=200)
    sponsors = models.CharField(max_length=300, blank=True)
    description = models.TextField()

    thumbnail = models.ImageField(
        upload_to="activities/thumbnails/", blank=True, null=True,
        validators=[validate_image_extension, validate_image_size],
    )
    youtube_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="activities",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Activities"

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


class ActivityMedia(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(
        upload_to="activities/gallery/", blank=True, null=True,
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
        return self.caption or f"Media for {self.activity.title}"