from django.contrib import admin
from .models import Activity, ActivityMedia


class ActivityMediaInline(admin.TabularInline):
    model = ActivityMedia
    extra = 1


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "activity_type", "date", "is_published")
    list_filter = ("activity_type", "is_published")
    inlines = [ActivityMediaInline]