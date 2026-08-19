from django import forms
from django.forms import inlineformset_factory
from .models import Achievement, AchievementMedia


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ["title", "description", "thumbnail", "youtube_url", "is_published"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "is_published":
                continue
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-input".strip()


AchievementMediaFormSet = inlineformset_factory(
    Achievement, AchievementMedia,
    fields=["image", "youtube_url", "caption"],
    extra=3, can_delete=True,
)

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ["title", "description", "thumbnail", "youtube_url", "is_published", "is_featured", "display_order"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in ("is_published", "is_featured"):
                continue
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} form-input".strip()