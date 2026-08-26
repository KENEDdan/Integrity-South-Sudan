from django import forms
from django.forms import inlineformset_factory
from apps.core.forms import set_file_accept_attrs
from .models import Activity, ActivityMedia


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "title", "activity_type", "date", "venue", "sponsors",
            "description", "thumbnail", "youtube_url", "is_published",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "is_published":
                continue
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-input".strip()
        set_file_accept_attrs(self)


ActivityMediaFormSet = inlineformset_factory(
    Activity, ActivityMedia,
    fields=["image", "youtube_url", "caption"],
    extra=3, can_delete=True,
    widgets={"image": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp,.gif"})},
)