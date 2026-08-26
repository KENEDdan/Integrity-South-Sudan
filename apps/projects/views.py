from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from apps.notifications.utils import notify_role
from .models import Project, Donor
from .forms import (
    ProjectForm, DonorForm, BeneficiaryRecordForm, MEIndicatorForm,
    FieldReportForm, IssueForm, IssueResolveForm, ProjectTaskForm, ProjectDocumentForm,
)


@role_required("program_manager")
def project_list(request):
    projects = Project.objects.all()
    return render(request, "projects/project_list.html", {"projects": projects})


@role_required("program_manager")
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            log_action(request.user, "Created project", project.name)
            messages.success(request, f'"{project.name}" was created.')
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, "projects/project_form.html", {"form": form, "mode": "Add"})


@role_required("program_manager")
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated project", project.name)
            messages.success(request, f'"{project.name}" was updated.')
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/project_form.html", {"form": form, "mode": "Edit", "project": project})


@role_required("program_manager")
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, "projects/project_detail.html", {"project": project})


@role_required("program_manager")
def beneficiary_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = BeneficiaryRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.project = project
            record.recorded_by = request.user
            record.save()
            messages.success(request, "Beneficiary record added.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = BeneficiaryRecordForm()
    return render(request, "projects/simple_form.html", {
        "form": form, "title": f"Add Beneficiary Record — {project.name}",
    })


@role_required("program_manager")
def indicator_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = MEIndicatorForm(request.POST)
        if form.is_valid():
            indicator = form.save(commit=False)
            indicator.project = project
            indicator.save()
            messages.success(request, "Indicator added.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = MEIndicatorForm()
    return render(request, "projects/simple_form.html", {
        "form": form, "title": f"Add M&E Indicator — {project.name}",
    })


@role_required("program_manager")
def field_report_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = FieldReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            report.submitted_by = request.user
            report.save()
            messages.success(request, "Field report submitted.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = FieldReportForm()
    return render(request, "projects/simple_form.html", {
        "form": form, "title": f"Submit Field Report — {project.name}", "enctype": True,
    })


@role_required("program_manager")
def field_report_mark_reviewed(request, pk, report_pk):
    project = get_object_or_404(Project, pk=pk)
    report = get_object_or_404(project.field_reports, pk=report_pk)
    if request.method == "POST":
        report.status = "reviewed"
        report.save(update_fields=["status"])
        messages.success(request, "Field report marked as reviewed.")
    return redirect("projects:project_detail", pk=project.pk)


@role_required("program_manager")
def issue_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.project = project
            issue.raised_by = request.user
            issue.save()
            log_action(request.user, "Raised project issue", f"{project.name}: {issue.title}")
            messages.success(request, "Issue logged.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = IssueForm()
    return render(request, "projects/simple_form.html", {"form": form, "title": f"Log Issue — {project.name}"})


@role_required("program_manager")
def issue_resolve(request, pk, issue_pk):
    project = get_object_or_404(Project, pk=pk)
    issue = get_object_or_404(project.issues, pk=issue_pk)
    if request.method == "POST":
        form = IssueResolveForm(request.POST)
        if form.is_valid():
            issue.resolution_notes = form.cleaned_data["resolution_notes"]
            issue.status = "resolved"
            issue.resolved_at = timezone.now()
            issue.save()
            messages.success(request, "Issue resolved.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = IssueResolveForm()
    return render(request, "projects/simple_form.html", {"form": form, "title": f"Resolve Issue — {issue.title}"})


@role_required("program_manager")
def task_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            messages.success(request, "Task added.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectTaskForm()
    return render(request, "projects/simple_form.html", {"form": form, "title": f"Add Task — {project.name}"})


@role_required("program_manager")
def task_complete(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(project.tasks, pk=task_pk)
    if request.method == "POST":
        task.status = "completed"
        task.save(update_fields=["status"])
        messages.success(request, "Task marked complete.")
    return redirect("projects:project_detail", pk=project.pk)


@role_required("program_manager")
def document_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user
            document.save()
            messages.success(request, "Document uploaded.")
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectDocumentForm()
    return render(request, "projects/simple_form.html", {
        "form": form, "title": f"Upload Document — {project.name}", "enctype": True,
    })


@role_required("program_manager")
def donor_list(request):
    donors = Donor.objects.all()
    donor_stats = []
    for donor in donors:
        donor_projects = donor.projects.all()
        by_currency = {}
        for p in donor_projects:
            entry = by_currency.setdefault(p.budget_currency, {"budget": 0, "spent": 0})
            entry["budget"] += p.budget_amount
            entry["spent"] += p.spent_amount
        donor_stats.append({
            "donor": donor,
            "project_count": donor_projects.count(),
            "by_currency": by_currency,
        })
    return render(request, "projects/donor_list.html", {"donor_stats": donor_stats})


@role_required("program_manager")
def donor_add(request):
    if request.method == "POST":
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Donor added.")
            return redirect("projects:donor_list")
    else:
        form = DonorForm()
    return render(request, "projects/simple_form.html", {"form": form, "title": "Add Donor"})