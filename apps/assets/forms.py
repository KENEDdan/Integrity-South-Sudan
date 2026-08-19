from django import forms
from .models import Asset, AssetLog


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ["name", "asset_type", "identifier", "assigned_to", "status", "purchase_date", "notes"]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"


class AssetLogForm(forms.ModelForm):
    class Meta:
        model = AssetLog
        fields = ["log_type", "date", "description", "cost", "currency"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"