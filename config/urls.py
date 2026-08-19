from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.newsfeed.urls", namespace="newsfeed")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("hr/", include("apps.hr.urls", namespace="hr")),
    path("finance/", include("apps.finance.urls", namespace="finance")),
    path("notifications/", include("apps.notifications.urls", namespace="notifications")),
    path("audit/", include("apps.audit.urls", namespace="audit")),
    path("achievements/", include("apps.achievements.urls", namespace="achievements")),
    path("activities/", include("apps.activities.urls", namespace="activities")),
    path("projects/", include("apps.projects.urls", namespace="projects")),
    path("reports/", include("apps.reports.urls", namespace="reports")),
    path("media-library/", include("apps.media_library.urls", namespace="media_library")),
    path("partners/", include("apps.partners.urls", namespace="partners")),
    path("leadership/", include("apps.leadership.urls", namespace="leadership")),
    path("contact/", include("apps.contact.urls", namespace="contact")),
    path("podcasts/", include("apps.podcasts.urls", namespace="podcasts")),
    path("about/", include("apps.about.urls", namespace="about")),
    path("donate/", include("apps.donations.urls", namespace="donations")),
    path("procurement/", include("apps.procurement.urls", namespace="procurement")),
    path("assets/", include("apps.assets.urls", namespace="assets")),
    path("field-data/", include("apps.field_data.urls", namespace="field_data")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)