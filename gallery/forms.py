from django import forms
from .models import Gallery, GalleryImage
from media_manager.fields import MediaFKField
from media_manager.models import Media

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'media_type', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter gallery title'}),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class GalleryImageForm(forms.ModelForm):
    image_media = MediaFKField()

    class Meta:
        model = GalleryImage
        fields = ['title', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter image title (optional)'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class ImageAddForm(forms.Form):
    image_media = MediaFKField(required=True)
