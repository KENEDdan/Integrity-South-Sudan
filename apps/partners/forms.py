from django import forms
from apps.core.forms import set_file_accept_attrs
from .models import Partner, PartnerRequest


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ["name", "logo", "base_address", "contact_address", "partnering_on", "validity_note", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "is_active":
                continue
            field.widget.attrs["class"] = "form-input"
        set_file_accept_attrs(self)


class PartnerRequestForm(forms.ModelForm):
    # Honeypot: invisible to real visitors, but simple bots fill in every
    # field they find. A non-empty value here means "not a human" — see
    # apps/partners/views.py, which silently drops the submission.
    website = forms.CharField(required=False, label="", widget=forms.TextInput(attrs={
        "autocomplete": "off", "tabindex": "-1", "class": "hp-field", "aria-hidden": "true",
    }))

    class Meta:
        model = PartnerRequest
        fields = [
            "organization_name", "logo", "address", "contact_email", "contact_phone",
            "registration_documents", "reason", "contract_validity",
        ]
        widgets = {"reason": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "website":
                field.widget.attrs["class"] = "form-input"
        set_file_accept_attrs(self)


class PartnerRequestDecisionForm(forms.Form):
    DECISION_CHOICES = [("approve", "Approve"), ("info", "Request More Information"), ("decline", "Decline")]
    decision = forms.ChoiceField(choices=DECISION_CHOICES, widget=forms.RadioSelect)
    admin_notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "class": "form-input"}), required=False)