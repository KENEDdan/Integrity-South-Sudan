from django import forms
from apps.accounts.models import Role


class AnnouncementForm(forms.Form):
    TARGET_CHOICES = [("all", "All Admins")] + list(Role.choices)
    target = forms.ChoiceField(choices=TARGET_CHOICES, label="Send to")
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label="Message")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target"].widget.attrs["class"] = "form-input"
        self.fields["message"].widget.attrs["class"] = "form-input"