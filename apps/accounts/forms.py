from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import User


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-input", "placeholder": "Username", "autofocus": True
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-input", "placeholder": "Password"
        })


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})


class AdminAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone_number", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"