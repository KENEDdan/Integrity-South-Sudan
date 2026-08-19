from django import forms
from .models import FinancialRequest, Transaction, AccountType


class FinancialRequestForm(forms.ModelForm):
    class Meta:
        model = FinancialRequest
        fields = ["amount", "currency", "category", "reason"]
        widgets = {"reason": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"


class ForwardRequestForm(forms.Form):
    finance_notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-input"}),
        required=False, label="Notes for Super Admin (optional)",
    )


class SuperAdminDecisionForm(forms.Form):
    DECISION_CHOICES = [("approve", "Approve"), ("info", "Request More Information"), ("decline", "Decline")]
    decision = forms.ChoiceField(choices=DECISION_CHOICES, widget=forms.RadioSelect)
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-input"}),
        label="Notes / reason (required for info request or decline)", required=False,
    )


class AdditionalInfoForm(forms.Form):
    additional_info = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-input"}), label="Additional information",
    )


class DisbursementForm(forms.Form):
    account_type = forms.ChoiceField(choices=AccountType.choices, label="Pay from")


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "transaction_type", "account_type", "currency", "amount",
            "income_source", "expense_category", "related_project", "description", "date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"