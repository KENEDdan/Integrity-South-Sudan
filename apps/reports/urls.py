from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("org-overview/", views.org_overview, name="org_overview"),
]