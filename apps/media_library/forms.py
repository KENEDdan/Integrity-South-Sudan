from django import forms
from apps.core.forms import set_file_accept_attrs
from .models import MediaResource


class MediaResourceForm(forms.ModelForm):
    class Meta:
        model = MediaResource
        fields = ["title", "resource_type", "file", "external_url", "tags"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-input".strip()
        set_file_accept_attrs(self)