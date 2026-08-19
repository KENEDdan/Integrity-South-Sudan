from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("add/", views.project_create, name="project_create"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("<int:pk>/edit/", views.project_edit, name="project_edit"),

    path("<int:pk>/beneficiaries/add/", views.beneficiary_add, name="beneficiary_add"),
    path("<int:pk>/indicators/add/", views.indicator_add, name="indicator_add"),
    path("<int:pk>/reports/add/", views.field_report_add, name="field_report_add"),
    path("<int:pk>/reports/<int:report_pk>/reviewed/", views.field_report_mark_reviewed, name="field_report_mark_reviewed"),
    path("<int:pk>/issues/add/", views.issue_add, name="issue_add"),
    path("<int:pk>/issues/<int:issue_pk>/resolve/", views.issue_resolve, name="issue_resolve"),
    path("<int:pk>/tasks/add/", views.task_add, name="task_add"),
    path("<int:pk>/tasks/<int:task_pk>/complete/", views.task_complete, name="task_complete"),
    path("<int:pk>/documents/add/", views.document_add, name="document_add"),

    path("donors/", views.donor_list, name="donor_list"),
    path("donors/add/", views.donor_add, name="donor_add"),
]