from django.urls import path
from . import views

app_name = "hr"

urlpatterns = [
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/add/", views.staff_create, name="staff_create"),
    path("staff/<int:pk>/", views.staff_detail, name="staff_detail"),
    path("staff/<int:pk>/edit/", views.staff_edit, name="staff_edit"),

    path("staff/<int:pk>/leave/add/", views.leave_add, name="leave_add"),
    path("staff/<int:pk>/leave/<int:leave_pk>/decide/", views.leave_decide, name="leave_decide"),
    path("leave/", views.leave_queue, name="leave_queue"),
    path("timesheets/", views.timesheets, name="timesheets"),
    path("timesheets/<int:record_pk>/toggle/", views.timesheet_toggle, name="timesheet_toggle"),

    path("jobs/", views.job_list, name="job_list"),
    path("jobs/add/", views.job_add, name="job_add"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/applicants/add/", views.applicant_add, name="applicant_add"),
    path("jobs/<int:pk>/applicants/<int:applicant_pk>/stage/", views.applicant_stage_update, name="applicant_stage_update"),
    path("applicants/<int:pk>/resume/", views.resume_download, name="resume_download"),

    path("compliance/", views.compliance_dashboard, name="compliance_dashboard"),
    path("staff/<int:pk>/training/add/", views.training_add, name="training_add"),
    path("staff/<int:pk>/documents/add/", views.document_add, name="document_add"),
    path("documents/<int:pk>/download/", views.document_download, name="document_download"),

    path("payroll/", views.payroll_list, name="payroll_list"),
    path("payroll/add/", views.payroll_add, name="payroll_add"),

    path("policies/", views.policy_list, name="policy_list"),
    path("policies/add/", views.policy_add, name="policy_add"),
    path("policies/<int:pk>/download/", views.policy_download, name="policy_download"),
]