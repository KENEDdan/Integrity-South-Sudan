from django import forms
from .models import ContactInfo, NewsletterSubscriber


class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        exclude = ["updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"


class NewsletterSubscriberForm(forms.ModelForm):
    # Honeypot — see apps/donations/forms.py for the same pattern.
    website = forms.CharField(required=False, label="", widget=forms.TextInput(attrs={
        "autocomplete": "off", "tabindex": "-1", "class": "hp-field", "aria-hidden": "true",
    }))

    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
        widgets = {"email": forms.EmailInput(attrs={
            "class": "form-input", "placeholder": "Your email address", "required": True,
        })}