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
            'media_type': forms.Select(
                attrs={'class': 'form-control'},
                choices=[
                    (Gallery.MEDIA_TYPE_IMAGE, 'Image'),
                    (Gallery.MEDIA_TYPE_VIDEO, 'Video'),
                ]
            ),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class GalleryImageForm(forms.ModelForm):
    image_media = MediaFKField(required=False)

    class Meta:
        model = GalleryImage
        fields = ['title', 'description', 'youtube_url', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter image title (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Video description'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class ImageAddForm(forms.Form):
    image_media = MediaFKField(required=True)
