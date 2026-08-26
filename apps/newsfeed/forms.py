from django import forms
from django.forms import inlineformset_factory
from apps.core.forms import set_file_accept_attrs
from .models import NewsPost, NewsMedia, DOCUMENT_REQUIRED_CATEGORIES


class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = [
            "title", "category", "brief_description", "body",
            "thumbnail", "youtube_url", "document", "is_published", "scheduled_for", "display_until",
        ]
        widgets = {
            "brief_description": forms.Textarea(attrs={"rows": 2}),
            "body": forms.Textarea(attrs={"rows": 8}),
            "scheduled_for": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "display_until": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "is_published":
                continue
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-input".strip()
        set_file_accept_attrs(self)

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        # FileField.clean() already falls back to the existing file on an
        # unchanged edit, so this also covers "don't re-require it on save".
        if category in DOCUMENT_REQUIRED_CATEGORIES and not cleaned_data.get("document"):
            self.add_error("document", "A PDF document is required for this category.")
        return cleaned_data


NewsMediaFormSet = inlineformset_factory(
    NewsPost, NewsMedia,
    fields=["image", "youtube_url", "caption"],
    extra=3, can_delete=True,
    widgets={"image": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp,.gif"})},
)
