from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.validators import validate_document_extension, validate_document_size


class ThematicArea(models.TextChoices):
    GOVERNANCE = "governance", "Democracy & Good Governance"
    LIVELIHOOD = "livelihood", "Livelihood"
    ENVIRONMENT = "environment", "Environmental Protection & Climate Change"
    MEDIA_ADVOCACY = "media_advocacy", "Media Advocacy"
    PROTECTION_GBV = "protection_gbv", "Protection & GBV"
    PEACE_SECURITY = "peace_security", "Peace and Security"


class ProjectStatus(models.TextChoices):
    PLANNING = "planning", "Planning"
    ACTIVE = "active", "Active"
    ON_HOLD = "on_hold", "On Hold"
    COMPLETED = "completed", "Completed"


class Currency(models.TextChoices):
    USD = "USD", "US Dollar"
    SSP = "SSP", "South Sudanese Pound"


class Donor(models.Model):
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=150, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200)
    thematic_area = models.CharField(max_length=30, choices=ThematicArea.choices)
    description = models.TextField()
    location = models.CharField(max_length=200, help_text="e.g. Central Equatoria State, Juba County")
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNING)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    donor = models.ForeignKey(Donor, null=True, blank=True, on_delete=models.SET_NULL, related_name="projects")
    budget_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    budget_currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)

    program_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_projects",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="projects_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def is_overdue(self):
        return bool(
            self.end_date and self.end_date < timezone.now().date() and self.status != ProjectStatus.COMPLETED
        )

    @property
    def spent_amount(self):
        total = self.expense_transactions.filter(transaction_type="expense").aggregate(
            total=models.Sum("amount")
        )["total"]
        return total or 0

    @property
    def budget_remaining(self):
        return self.budget_amount - self.spent_amount

    @property
    def percent_spent(self):
        if not self.budget_amount:
            return 0
        return round((self.spent_amount / self.budget_amount) * 100, 1)


class BeneficiaryRecord(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="beneficiary_records")
    period_label = models.CharField(max_length=50, help_text="e.g. July 2026 or Q3 2026")
    period_date = models.DateField(
        null=True, blank=True, help_text="Any date within the reporting period — used for year-to-date totals.",
    )
    target_count = models.PositiveIntegerField(default=0)
    actual_count = models.PositiveIntegerField(default=0)
    male_count = models.PositiveIntegerField(default=0)
    female_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.name} — {self.period_label}"


class DataCollectionStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"


class MEIndicator(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="indicators")
    indicator_name = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, help_text="e.g. # trained, % completion")
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    actual_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    period_label = models.CharField(max_length=50, blank=True)
    data_collection_status = models.CharField(
        max_length=20, choices=DataCollectionStatus.choices, default=DataCollectionStatus.NOT_STARTED,
    )
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["indicator_name"]

    def __str__(self):
        return f"{self.indicator_name} ({self.project.name})"

    @property
    def percent_achieved(self):
        if not self.target_value:
            return 0
        return round((self.actual_value / self.target_value) * 100, 1)


class FieldReportStatus(models.TextChoices):
    PENDING = "pending", "Pending Review"
    REVIEWED = "reviewed", "Reviewed"


class FieldReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="field_reports")
    title = models.CharField(max_length=200)
    report_date = models.DateField()
    summary = models.TextField()
    attachment = models.FileField(
        upload_to="projects/field_reports/", blank=True, null=True,
        validators=[validate_document_extension, validate_document_size],
    )
    status = models.CharField(max_length=20, choices=FieldReportStatus.choices, default=FieldReportStatus.PENDING)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-report_date"]

    def __str__(self):
        return self.title


class IssueCategory(models.TextChoices):
    FIELD_CHALLENGE = "field_challenge", "Field Challenge"
    PARTNER_DELAY = "partner_delay", "Partner Delay"
    OTHER = "other", "Other"


class IssueStatus(models.TextChoices):
    OPEN = "open", "Open"
    RESOLVED = "resolved", "Resolved"


class Issue(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=IssueCategory.choices)
    status = models.CharField(max_length=20, choices=IssueStatus.choices, default=IssueStatus.OPEN)
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="issues_raised",
    )
    resolution_notes = models.TextField(blank=True)
    raised_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-raised_at"]

    def __str__(self):
        return self.title


class TaskStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"


class ProjectTask(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_staff = models.ForeignKey(
        "hr.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="project_tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return bool(
            self.due_date and self.due_date < timezone.now().date() and self.status != TaskStatus.COMPLETED
        )


class DocumentType(models.TextChoices):
    PROPOSAL = "proposal", "Proposal"
    LOGFRAME = "logframe", "Logframe"
    WORKPLAN = "workplan", "Workplan"
    OTHER = "other", "Other"


class ProjectDocument(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    file = models.FileField(
        upload_to="projects/documents/",
        validators=[validate_document_extension, validate_document_size],
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title