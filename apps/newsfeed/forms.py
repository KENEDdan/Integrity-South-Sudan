from django import forms
from django.forms import inlineformset_factory
from .models import NewsPost, NewsMedia


class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = [
            "title", "category", "brief_description", "body",
            "thumbnail", "youtube_url", "is_published", "scheduled_for", "display_until",
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


NewsMediaFormSet = inlineformset_factory(
    NewsPost, NewsMedia,
    fields=["image", "youtube_url", "caption"],
    extra=3, can_delete=True,
)