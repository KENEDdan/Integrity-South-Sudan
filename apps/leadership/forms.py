from django import forms
from .models import Leader


class LeaderForm(forms.ModelForm):
    class Meta:
        model = Leader
        fields = ["name", "title", "qualifications", "address", "biography", "photo", "display_order", "is_published"]
        widgets = {
            "qualifications": forms.Textarea(attrs={"rows": 3}),
            "biography": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "is_published":
                continue
            field.widget.attrs["class"] = "form-input"