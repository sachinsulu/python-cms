# social/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Social
from media_manager.fields import MediaFKField  # ← replaces inline IntegerField


class SocialForm(forms.ModelForm):

    image_media = MediaFKField()  # ← replaces manual IntegerField + clean_image_media

    class Meta:
        model  = Social
        fields = ['title', 'link', 'icon', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title'}),
            'link':  forms.TextInput(attrs={'placeholder': 'https://example.com or /relative/path/'}),
            'icon':  forms.TextInput(attrs={'placeholder': 'e.g. fa-brands fa-instagram'}),
        }

    def clean_link(self):
        link = self.cleaned_data.get('link', '').strip()
        if link and not link.startswith(('http://', 'https://', '/')):
            raise ValidationError(
                "Enter a valid URL (https://...) or a relative path (/page/)."
            )
        return link

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('image_media')
        if media is not None:
            instance.image = media
        if commit:
            instance.save()
        return instance