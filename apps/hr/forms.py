from django import forms
from .models import (
    Staff, LeaveRequest, JobOpening, Applicant, TrainingRecord,
    StaffDocument, PayrollRun, PolicyDocument,
)


def _styled(form):
    for field in form.fields.values():
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} form-input".strip()


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            "full_name", "date_of_birth", "gender", "national_id_or_passport",
            "phone_number", "email", "residential_address",
            "next_of_kin_name", "next_of_kin_phone", "next_of_kin_relationship",
            "position", "department", "employment_type", "date_of_joining",
            "contract_end_date", "probation_end_date", "status",
            "salary_amount", "salary_currency", "pay_frequency",
            "bank_name", "bank_account_number", "photo",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "date_of_joining": forms.DateInput(attrs={"type": "date"}),
            "contract_end_date": forms.DateInput(attrs={"type": "date"}),
            "probation_end_date": forms.DateInput(attrs={"type": "date"}),
            "residential_address": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class LeaveDecisionForm(forms.Form):
    DECISION_CHOICES = [("approve", "Approve"), ("decline", "Decline")]
    decision = forms.ChoiceField(choices=DECISION_CHOICES, widget=forms.RadioSelect)
    decision_notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "class": "form-input"}), required=False)


class JobOpeningForm(forms.ModelForm):
    class Meta:
        model = JobOpening
        fields = ["title", "department", "description", "posted_date", "closing_date", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "posted_date": forms.DateInput(attrs={"type": "date"}),
            "closing_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ["full_name", "email", "phone", "resume", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class ApplicantStageForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ["stage", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class TrainingRecordForm(forms.ModelForm):
    class Meta:
        model = TrainingRecord
        fields = ["training_name", "due_date", "completed_date", "notes"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "completed_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class StaffDocumentForm(forms.ModelForm):
    class Meta:
        model = StaffDocument
        fields = ["document_type", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class PayrollRunForm(forms.ModelForm):
    class Meta:
        model = PayrollRun
        fields = ["period_label", "status", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class PolicyDocumentForm(forms.ModelForm):
    class Meta:
        model = PolicyDocument
        fields = ["title", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)