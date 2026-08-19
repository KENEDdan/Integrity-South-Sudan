from django.db import models


class ContactInfo(models.Model):
    organization_name = models.CharField(max_length=200, default="Integrity South Sudan")
    physical_address = models.CharField(max_length=255, blank=True)
    postal_address = models.CharField(max_length=255, blank=True)
    phone_primary = models.CharField(max_length=30, blank=True)
    phone_secondary = models.CharField(max_length=30, blank=True)
    email_general = models.EmailField(blank=True)
    email_media = models.EmailField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    office_hours = models.CharField(max_length=200, blank=True)
    map_embed_url = models.URLField(blank=True, help_text="Google Maps embed link, optional")
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Contact Information"