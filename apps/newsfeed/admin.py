from django.contrib import admin
from .models import NewsPost, NewsMedia


class NewsMediaInline(admin.TabularInline):
    model = NewsMedia
    extra = 1


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("category", "is_published")
    inlines = [NewsMediaInline]