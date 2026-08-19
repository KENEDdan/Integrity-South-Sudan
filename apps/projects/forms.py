from django import forms
from .models import (
    Project, Donor, BeneficiaryRecord, MEIndicator, FieldReport, Issue, ProjectTask, ProjectDocument,
)


def _styled(form):
    for field in form.fields.values():
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} form-input".strip()


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ["name", "contact_person", "contact_email", "contact_phone", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name", "thematic_area", "description", "location", "status",
            "start_date", "end_date", "donor", "budget_amount", "budget_currency", "program_manager",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import User, Role
        self.fields["program_manager"].queryset = User.objects.filter(role=Role.PROGRAM_MANAGER, is_active=True)
        _styled(self)


class BeneficiaryRecordForm(forms.ModelForm):
    class Meta:
        model = BeneficiaryRecord
        fields = ["period_label", "period_date", "target_count", "actual_count", "male_count", "female_count", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
            "period_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class MEIndicatorForm(forms.ModelForm):
    class Meta:
        model = MEIndicator
        fields = [
            "indicator_name", "unit", "target_value", "actual_value",
            "period_label", "data_collection_status", "notes",
        ]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class FieldReportForm(forms.ModelForm):
    class Meta:
        model = FieldReport
        fields = ["title", "report_date", "summary", "attachment"]
        widgets = {
            "report_date": forms.DateInput(attrs={"type": "date"}),
            "summary": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["title", "description", "category"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class IssueResolveForm(forms.Form):
    resolution_notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "class": "form-input"}))


class ProjectTaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = ["title", "description", "assigned_staff", "due_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ["title", "document_type", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)