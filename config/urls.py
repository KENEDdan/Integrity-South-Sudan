import re

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as serve_static

# Internal/staff-only apps that should never show up in search results.
_DISALLOWED_PATHS = [
    "admin",
    "accounts",
    "hr",
    "finance",
    "notifications",
    "audit",
    "reports",
    "procurement",
    "assets",
    "field-data",
]


def robots_txt(request):
    lines = ["User-agent: *"]
    lines += [f"Disallow: /{path}/" for path in _DISALLOWED_PATHS]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


urlpatterns = [
    path("robots.txt", robots_txt),
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
else:
    # MEDIA_URL is otherwise never served outside DEBUG. Only expose the
    # subpaths that are genuinely public content — everything else (resumes,
    # donation proofs, partner/project documents, the internal media
    # library, ...) stays reachable only through its auth-gated FileResponse
    # view, same as before.
    _PUBLIC_MEDIA_PREFIXES = [
        "newsfeed/thumbnails", "newsfeed/gallery", "newsfeed/documents",
        "achievements/thumbnails", "achievements/gallery",
        "activities/thumbnails", "activities/gallery",
        "partners/logos", "leadership", "podcasts/thumbnails",
    ]
    urlpatterns += [
        re_path(
            r"^media/(?P<path>(?:%s)/.*)$" % "|".join(re.escape(p) for p in _PUBLIC_MEDIA_PREFIXES),
            serve_static,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]