from django.contrib import admin
from .models import ContactInfo, NewsletterSubscriber

admin.site.register(ContactInfo)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "subscribed_at"]
    search_fields = ["email"]
    ordering = ["-subscribed_at"]