from django.contrib import admin
from .models import Achievement, AchievementMedia


class AchievementMediaInline(admin.TabularInline):
    model = AchievementMedia
    extra = 1


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created_at")
    inlines = [AchievementMediaInline]