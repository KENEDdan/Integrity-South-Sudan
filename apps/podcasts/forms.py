from django import forms
from apps.core.forms import set_file_accept_attrs
from .models import Podcast


class PodcastForm(forms.ModelForm):
    class Meta:
        model = Podcast
        fields = ["title", "content", "video_url", "thumbnail", "is_published"]
        widgets = {"content": forms.Textarea(attrs={"rows": 6})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "is_published":
                continue
            field.widget.attrs["class"] = "form-input"
        set_file_accept_attrs(self)