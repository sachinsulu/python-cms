from django import forms
from .models import Slideshow
from media_manager.fields import MediaFKField


class SlideshowForm(forms.ModelForm):
    image_media = MediaFKField()

    class Meta:
        model  = Slideshow
        fields = ['title', 'subtitle', 'content', 'active']
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'Title'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'Sub Title'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('image_media')
        if media is not None:
            instance.image = media
        if commit:
            instance.save()
        return instance