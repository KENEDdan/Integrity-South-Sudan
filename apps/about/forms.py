from django import forms
from .models import AboutUs


class AboutUsForm(forms.ModelForm):
    class Meta:
        model = AboutUs
        exclude = ["updated_at"]
        widgets = {
            "executive_summary": forms.Textarea(attrs={"rows": 6}),
            "vision": forms.Textarea(attrs={"rows": 2}),
            "mission": forms.Textarea(attrs={"rows": 4}),
            "core_values": forms.Textarea(attrs={"rows": 6}),
            "thematic_areas": forms.Textarea(attrs={"rows": 8}),
            "strategic_objectives": forms.Textarea(attrs={"rows": 6}),
            "key_achievements_summary": forms.Textarea(attrs={"rows": 4}),
            "partners_note": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"