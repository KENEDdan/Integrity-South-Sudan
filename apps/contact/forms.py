from django import forms
from .models import ContactInfo


class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        exclude = ["updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"