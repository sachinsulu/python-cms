# testimonials/forms.py
from django import forms
from .models import Testimonial
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.core.exceptions import ValidationError
from media_manager.fields import MediaFKField


class TestimonialForm(forms.ModelForm):
    remove_image = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial='0'
    )
    image_media = MediaFKField()

    class Meta:
        model = Testimonial
        fields = [
            'title', 'name', 'content', 'rating',
            'active', 'linksrc', 'country', 'via_type',
        ]
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'Testimonial title'}),
            'name':     forms.TextInput(attrs={'placeholder': 'Reviewer name'}),
            'content':  CKEditorUploadingWidget(),
            'rating':   forms.Select(choices=Testimonial.RATING_CHOICES),
            'linksrc':  forms.URLInput(attrs={'placeholder': 'https://'}),
            'country':  forms.TextInput(attrs={'placeholder': 'Country'}),
            'via_type': forms.TextInput(
                attrs={'placeholder': 'e.g. Google, TripAdvisor'}
            ),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('image_media')
        if media is not None:
            instance.image = media
        if commit:
            instance.save()
        return instance