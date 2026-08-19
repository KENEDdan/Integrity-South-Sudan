from django import forms
from .models import Vendor, Requisition, PurchaseOrder, Delivery


def _styled(form):
    for field in form.fields.values():
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} form-input".strip()


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ["name", "category", "contact_person", "phone", "email", "address", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2}), "address": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ["related_project", "items_description", "justification", "estimated_cost", "currency"]
        widgets = {
            "items_description": forms.Textarea(attrs={"rows": 3}),
            "justification": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class RequisitionDecisionForm(forms.Form):
    DECISION_CHOICES = [("approve", "Approve"), ("decline", "Decline")]
    decision = forms.ChoiceField(choices=DECISION_CHOICES, widget=forms.RadioSelect)
    decision_notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "class": "form-input"}), required=False)


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["vendor", "total_amount", "currency"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styled(self)


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ["delivered_date", "condition_notes", "is_complete"]
        widgets = {
            "delivered_date": forms.DateInput(attrs={"type": "date"}),
            "condition_notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "is_complete":
                continue
            field.widget.attrs["class"] = "form-input"