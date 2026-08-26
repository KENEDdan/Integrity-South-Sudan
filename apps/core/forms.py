from django import forms
from django.core.validators import FileExtensionValidator


def set_file_accept_attrs(form):
    """Set an `accept` attribute on file/image inputs from their model
    field's FileExtensionValidator, so the OS file picker itself filters by
    extension — the validator stays the single source of truth.

    Reads the *model* field's validators rather than the form field's:
    Django's File/ImageField.formfield() doesn't forward a model field's
    custom validators to the form field it builds (they still apply, but
    only later via ModelForm._post_clean() -> instance.full_clean()).
    """
    model = getattr(getattr(form, "_meta", None), "model", None)
    if model is None:
        return
    for name, field in form.fields.items():
        if not isinstance(field, (forms.FileField, forms.ImageField)):
            continue
        try:
            model_field = model._meta.get_field(name)
        except Exception:
            continue
        for validator in getattr(model_field, "validators", []):
            if isinstance(validator, FileExtensionValidator):
                field.widget.attrs["accept"] = ",".join(
                    f".{ext}" for ext in validator.allowed_extensions
                )
                break
