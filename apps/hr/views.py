from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from apps.accounts.decorators import role_required
from apps.audit.utils import log_action
from .models import (
    Staff, StaffStatus, LeaveRequest, LeaveStatus, TimesheetRecord,
    JobOpening, TrainingRecord, PayrollRun, PolicyDocument,
)
from .forms import (
    StaffForm, LeaveRequestForm, LeaveDecisionForm, JobOpeningForm, ApplicantForm,
    ApplicantStageForm, TrainingRecordForm, StaffDocumentForm, PayrollRunForm, PolicyDocumentForm,
)


@role_required("hr")
def staff_list(request):
    staff = Staff.objects.all()
    return render(request, "hr/staff_list.html", {"staff": staff})


@role_required("hr")
def staff_detail(request, pk):
    member = get_object_or_404(Staff, pk=pk)
    return render(request, "hr/staff_detail.html", {"member": member})


@role_required("hr")
def staff_create(request):
    if request.method == "POST":
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.created_by = request.user
            staff.save()
            log_action(request.user, "Added new staff member", f"{staff.full_name} ({staff.position})")
            messages.success(request, f"{staff.full_name} was added to staff records.")
            return redirect("hr:staff_detail", pk=staff.pk)
    else:
        form = StaffForm()
    return render(request, "hr/staff_form.html", {"form": form, "mode": "Add"})


@role_required("hr")
def staff_edit(request, pk):
    member = get_object_or_404(Staff, pk=pk)
    if request.method == "POST":
        form = StaffForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            log_action(request.user, "Updated staff record", member.full_name)
            messages.success(request, f"{member.full_name}'s record was updated.")
            return redirect("hr:staff_detail", pk=member.pk)
    else:
        form = StaffForm(instance=member)
    return render(request, "hr/staff_form.html", {"form": form, "mode": "Edit", "member": member})


@role_required("hr")
def leave_queue(request):
    pending = LeaveRequest.objects.filter(status=LeaveStatus.PENDING)
    return render(request, "hr/leave_queue.html", {"pending": pending})


@role_required("hr")
def leave_add(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.staff = staff
            leave.logged_by = request.user
            leave.save()
            messages.success(request, "Leave request logged.")
            return redirect("hr:staff_detail", pk=staff.pk)
    else:
        form = LeaveRequestForm()
    return render(request, "hr/simple_form.html", {"form": form, "title": f"Log Leave Request — {staff.full_name}"})


@role_required("hr")
def leave_decide(request, pk, leave_pk):
    staff = get_object_or_404(Staff, pk=pk)
    leave = get_object_or_404(staff.leave_requests, pk=leave_pk)
    if request.method == "POST":
        form = LeaveDecisionForm(request.POST)
        if form.is_valid():
            leave.status = LeaveStatus.APPROVED if form.cleaned_data["decision"] == "approve" else LeaveStatus.DECLINED
            leave.decision_notes = form.cleaned_data["decision_notes"]
            leave.decided_by = request.user
            leave.save()
            messages.success(request, "Leave decision recorded.")
            return redirect("hr:leave_queue")
    else:
        form = LeaveDecisionForm()
    return render(request, "hr/simple_form.html", {"form": form, "title": f"Decide Leave — {staff.full_name}"})


@role_required("hr")
def timesheets(request):
    today = timezone.now().date()
    period_label = today.strftime("%Y-%m")
    active_staff = Staff.objects.filter(status=StaffStatus.ACTIVE)
    for member in active_staff:
        TimesheetRecord.objects.get_or_create(staff=member, period_label=period_label)
    records = TimesheetRecord.objects.filter(period_label=period_label).select_related("staff")
    submitted_count = records.filter(submitted=True).count()
    percent = round((submitted_count / records.count()) * 100, 1) if records.count() else 0
    return render(request, "hr/timesheets.html", {
        "records": records, "period_label": period_label, "percent": percent,
    })


@role_required("hr")
def timesheet_toggle(request, record_pk):
    record = get_object_or_404(TimesheetRecord, pk=record_pk)
    record.submitted = not record.submitted
    record.submitted_on = timezone.now().date() if record.submitted else None
    record.save()
    return redirect("hr:timesheets")


@role_required("hr")
def job_list(request):
    jobs = JobOpening.objects.all()
    return render(request, "hr/job_list.html", {"jobs": jobs})


@role_required("hr")
def job_add(request):
    if request.method == "POST":
        form = JobOpeningForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            log_action(request.user, "Opened job posting", job.title)
            messages.success(request, f'"{job.title}" was posted.')
            return redirect("hr:job_detail", pk=job.pk)
    else:
        form = JobOpeningForm()
    return render(request, "hr/simple_form.html", {"form": form, "title": "New Job Opening"})


@role_required("hr")
def job_detail(request, pk):
    job = get_object_or_404(JobOpening, pk=pk)
    return render(request, "hr/job_detail.html", {"job": job})


@role_required("hr")
def applicant_add(request, pk):
    job = get_object_or_404(JobOpening, pk=pk)
    if request.method == "POST":
        form = ApplicantForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save(commit=False)
            applicant.job_opening = job
            applicant.save()
            messages.success(request, "Applicant added.")
            return redirect("hr:job_detail", pk=job.pk)
    else:
        form = ApplicantForm()
    return render(request, "hr/simple_form.html", {
        "form": form, "title": f"Add Applicant — {job.title}", "enctype": True,
    })


@role_required("hr")
def applicant_stage_update(request, pk, applicant_pk):
    job = get_object_or_404(JobOpening, pk=pk)
    applicant = get_object_or_404(job.applicants, pk=applicant_pk)
    if request.method == "POST":
        form = ApplicantStageForm(request.POST, instance=applicant)
        if form.is_valid():
            form.save()
            messages.success(request, "Applicant stage updated.")
            return redirect("hr:job_detail", pk=job.pk)
    else:
        form = ApplicantStageForm(instance=applicant)
    return render(request, "hr/simple_form.html", {"form": form, "title": f"Update Stage — {applicant.full_name}"})


@role_required("hr")
def compliance_dashboard(request):
    today = timezone.now().date()
    soon_60 = today + timedelta(days=60)
    soon_30 = today + timedelta(days=30)

    contracts_expiring = Staff.objects.filter(
        status=StaffStatus.ACTIVE, contract_end_date__isnull=False,
        contract_end_date__lte=soon_60, contract_end_date__gte=today,
    ).order_by("contract_end_date")

    probation_ending = Staff.objects.filter(
        status=StaffStatus.ACTIVE, probation_end_date__isnull=False,
        probation_end_date__lte=soon_30, probation_end_date__gte=today,
    ).order_by("probation_end_date")

    trainings_due = TrainingRecord.objects.filter(
        completed_date__isnull=True, due_date__lte=soon_30,
    ).select_related("staff").order_by("due_date")

    required_types = ["id_copy", "contract"]
    missing_docs = []
    for member in Staff.objects.filter(status=StaffStatus.ACTIVE):
        have = set(member.documents.values_list("document_type", flat=True))
        missing = [t for t in required_types if t not in have]
        if missing:
            missing_docs.append({"staff": member, "missing": missing})

    return render(request, "hr/compliance_dashboard.html", {
        "contracts_expiring": contracts_expiring,
        "probation_ending": probation_ending,
        "trainings_due": trainings_due,
        "missing_docs": missing_docs,
    })


@role_required("hr")
def training_add(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == "POST":
        form = TrainingRecordForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.staff = staff
            training.save()
            messages.success(request, "Training record added.")
            return redirect("hr:staff_detail", pk=staff.pk)
    else:
        form = TrainingRecordForm()
    return render(request, "hr/simple_form.html", {"form": form, "title": f"Add Training — {staff.full_name}"})


@role_required("hr")
def document_add(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == "POST":
        form = StaffDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.staff = staff
            document.uploaded_by = request.user
            document.save()
            messages.success(request, "Document uploaded.")
            return redirect("hr:staff_detail", pk=staff.pk)
    else:
        form = StaffDocumentForm()
    return render(request, "hr/simple_form.html", {
        "form": form, "title": f"Upload Document — {staff.full_name}", "enctype": True,
    })


@role_required("hr")
def payroll_list(request):
    runs = PayrollRun.objects.all()
    totals = {}
    for currency in ("USD", "SSP"):
        totals[currency] = Staff.objects.filter(
            status=StaffStatus.ACTIVE, salary_currency=currency,
        ).aggregate(total=Sum("salary_amount"))["total"] or 0
    return render(request, "hr/payroll_list.html", {"runs": runs, "totals": totals})


@role_required("hr")
def payroll_add(request):
    if request.method == "POST":
        form = PayrollRunForm(request.POST)
        if form.is_valid():
            run = form.save(commit=False)
            run.processed_by = request.user
            run.save()
            log_action(request.user, "Updated payroll status", f"{run.period_label}: {run.status}")
            messages.success(request, "Payroll run saved.")
            return redirect("hr:payroll_list")
    else:
        form = PayrollRunForm()
    return render(request, "hr/simple_form.html", {"form": form, "title": "New Payroll Run"})


@role_required("hr")
def policy_list(request):
    policies = PolicyDocument.objects.all()
    return render(request, "hr/policy_list.html", {"policies": policies})


@role_required("hr")
def policy_add(request):
    if request.method == "POST":
        form = PolicyDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.uploaded_by = request.user
            policy.save()
            messages.success(request, "Policy document uploaded.")
            return redirect("hr:policy_list")
    else:
        form = PolicyDocumentForm()
    return render(request, "hr/simple_form.html", {
        "form": form, "title": "Upload Policy Document", "enctype": True,
    })