from django import forms
from django.core.exceptions import ValidationError
from .models import Social


class SocialForm(forms.ModelForm):

    # Hidden field receives Media.pk from the JS picker
    image_media = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model  = Social
        fields = ['title', 'link', 'icon', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title'}),
            'link':  forms.TextInput(attrs={'placeholder': 'https://example.com or /relative/path/'}),
            'icon':  forms.TextInput(attrs={'placeholder': 'e.g. fa-brands fa-instagram'}),
        }

    def clean_link(self):
        """
        Validate link at form level rather than using URLField on the model.
        Accepts full URLs and relative paths (both are valid CMS link values).
        """
        link = self.cleaned_data.get('link', '').strip()
        if link and not link.startswith(('http://', 'https://', '/')):
            raise ValidationError(
                "Enter a valid URL (https://...) or a relative path (/page/)."
            )
        return link

    def clean_image_media(self):
        pk = self.cleaned_data.get('image_media')
        if not pk:
            return None
        from media_manager.models import Media
        try:
            return Media.objects.get(pk=pk)
        except Media.DoesNotExist:
            raise ValidationError(
                f"Selected media (id={pk}) no longer exists. "
                "Please choose a different file from the library."
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('image_media')
        # Only overwrite if picker submitted something —
        # preserves existing image when saving without touching image field
        if media is not None:
            instance.image = media
        if commit:
            instance.save()
        return instance