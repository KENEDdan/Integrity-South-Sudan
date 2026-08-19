from django import forms
from .models import Donation, DonationSettings


class DonationForm(forms.ModelForm):
    # Honeypot: invisible to real visitors, but simple bots fill in every
    # field they find. A non-empty value here means "not a human" — see
    # apps/donations/views.py, which silently drops the submission.
    website = forms.CharField(required=False, label="", widget=forms.TextInput(attrs={
        "autocomplete": "off", "tabindex": "-1", "class": "hp-field", "aria-hidden": "true",
    }))

    class Meta:
        model = Donation
        fields = ["donor_name", "donor_email", "donor_phone", "amount", "currency", "frequency", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "website":
                field.widget.attrs["class"] = "form-input"


class DonationSettingsForm(forms.ModelForm):
    class Meta:
        model = DonationSettings
        fields = ["bank_name", "account_name", "account_number", "branch", "swift_code", "mobile_money_note", "instructions"]
        widgets = {"instructions": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"