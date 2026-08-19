from django.conf import settings
from django.db import models


class SubmissionStatus(models.TextChoices):
    NEW = "new", "New"
    REVIEWED = "reviewed", "Reviewed"


class KoboSubmission(models.Model):
    form_uid = models.CharField(max_length=100, help_text="KoboToolBox form/asset ID")
    submission_id = models.CharField(max_length=100)
    raw_data = models.JSONField()
    related_project = models.ForeignKey(
        "projects.Project", null=True, blank=True, on_delete=models.SET_NULL, related_name="kobo_submissions",
    )
    status = models.CharField(max_length=20, choices=SubmissionStatus.choices, default=SubmissionStatus.NEW)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at"]
        unique_together = ["form_uid", "submission_id"]

    def __str__(self):
        return f"Kobo submission {self.submission_id} ({self.form_uid})"