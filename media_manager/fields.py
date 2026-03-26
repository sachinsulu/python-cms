# media_manager/fields.py
from django import forms
from django.core.exceptions import ValidationError


class MediaFKField(forms.IntegerField):
    """
    Hidden integer field that receives a Media.pk from the JS picker.
    - Empty/None  → returns None (field is not required)
    - Valid pk    → returns Media instance  
    - Invalid pk  → raises ValidationError

    Usage:
        from media_manager.fields import MediaFKField

        class MyForm(forms.ModelForm):
            image_media = MediaFKField()
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('widget', forms.HiddenInput())
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        if value is None:
            return None
        from media_manager.models import Media
        try:
            media = Media.objects.get(pk=value)
            if not media.active:
                raise ValidationError(
                    f"Selected media '{media.title}' is inactive and cannot be used here."
                )
            return media
        except Media.DoesNotExist:
            raise ValidationError(
                f"Selected media (id={value}) no longer exists. "
                "Please choose a different file from the library."
            )