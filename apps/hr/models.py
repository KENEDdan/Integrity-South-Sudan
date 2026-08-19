from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.validators import (
    validate_document_extension, validate_document_size,
    validate_image_extension, validate_image_size,
)


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full-Time"
    PART_TIME = "part_time", "Part-Time"
    CONTRACT = "contract", "Contract"
    VOLUNTEER = "volunteer", "Volunteer"
    INTERN = "intern", "Intern"


class StaffStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    ON_LEAVE = "on_leave", "On Leave"
    TERMINATED = "terminated", "Terminated"


class Currency(models.TextChoices):
    USD = "USD", "US Dollar"
    SSP = "SSP", "South Sudanese Pound"


class Staff(models.Model):
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female")], blank=True)
    national_id_or_passport = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    residential_address = models.CharField(max_length=255)

    next_of_kin_name = models.CharField(max_length=150, blank=True)
    next_of_kin_phone = models.CharField(max_length=30, blank=True)
    next_of_kin_relationship = models.CharField(max_length=50, blank=True)

    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices)
    date_of_joining = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StaffStatus.choices, default=StaffStatus.ACTIVE)

    salary_amount = models.DecimalField(max_digits=12, decimal_places=2)
    salary_currency = models.CharField(max_length=3, choices=Currency.choices)
    pay_frequency = models.CharField(
        max_length=20, choices=[("monthly", "Monthly"), ("weekly", "Weekly")], default="monthly",
    )

    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)

    photo = models.ImageField(
        upload_to="staff_photos/", blank=True, null=True,
        validators=[validate_image_extension, validate_image_size],
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="staff_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} — {self.position}"

    @property
    def is_on_approved_leave_today(self):
        today = timezone.now().date()
        return self.leave_requests.filter(status="approved", start_date__lte=today, end_date__gte=today).exists()


class LeaveType(models.TextChoices):
    ANNUAL = "annual", "Annual"
    SICK = "sick", "Sick"
    COMPASSIONATE = "compassionate", "Compassionate"
    MATERNITY = "maternity", "Maternity"
    PATERNITY = "paternity", "Paternity"
    UNPAID = "unpaid", "Unpaid"


class LeaveStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    DECLINED = "declined", "Declined"


class LeaveRequest(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=LeaveStatus.choices, default=LeaveStatus.PENDING)
    decision_notes = models.TextField(blank=True)
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="leave_requests_logged",
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="leave_requests_decided",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.staff.full_name} — {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"


class TimesheetRecord(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="timesheets")
    period_label = models.CharField(max_length=20, help_text="e.g. 2026-08")
    submitted = models.BooleanField(default=False)
    submitted_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-period_label"]
        unique_together = ["staff", "period_label"]

    def __str__(self):
        return f"{self.staff.full_name} — {self.period_label}"


class JobOpeningStatus(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"
    FILLED = "filled", "Filled"


class JobOpening(models.Model):
    title = models.CharField(max_length=150)
    department = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=JobOpeningStatus.choices, default=JobOpeningStatus.OPEN)
    posted_date = models.DateField()
    closing_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ApplicantStage(models.TextChoices):
    APPLIED = "applied", "Applied"
    SHORTLISTED = "shortlisted", "Shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled", "Interview Scheduled"
    INTERVIEWED = "interviewed", "Interviewed"
    OFFERED = "offered", "Offered"
    HIRED = "hired", "Hired"
    REJECTED = "rejected", "Rejected"


class Applicant(models.Model):
    job_opening = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="applicants")
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    resume = models.FileField(
        upload_to="hr/resumes/", blank=True, null=True,
        validators=[validate_document_extension, validate_document_size],
    )
    stage = models.CharField(max_length=30, choices=ApplicantStage.choices, default=ApplicantStage.APPLIED)
    notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.full_name} — {self.job_opening.title}"


class TrainingRecord(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="trainings")
    training_name = models.CharField(max_length=200)
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.training_name} — {self.staff.full_name}"

    @property
    def is_overdue(self):
        return bool(not self.completed_date and self.due_date < timezone.now().date())


class StaffDocumentType(models.TextChoices):
    ID_COPY = "id_copy", "National ID / Passport Copy"
    CONTRACT = "contract", "Signed Contract"
    CV = "cv", "CV / Resume"
    CERTIFICATE = "certificate", "Certificate"
    OTHER = "other", "Other"


class StaffDocument(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=StaffDocumentType.choices)
    file = models.FileField(
        upload_to="hr/staff_documents/",
        validators=[validate_document_extension, validate_document_size],
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.get_document_type_display()} — {self.staff.full_name}"


class PayrollStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"


class PayrollRun(models.Model):
    period_label = models.CharField(max_length=20, unique=True, help_text="e.g. 2026-08")
    status = models.CharField(max_length=20, choices=PayrollStatus.choices, default=PayrollStatus.NOT_STARTED)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_label"]

    def __str__(self):
        return f"Payroll {self.period_label} ({self.get_status_display()})"


class PolicyDocument(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to="hr/policies/",
        validators=[validate_document_extension, validate_document_size],
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title