# popup/forms.py
from django import forms
from django.core.exceptions import ValidationError
from media_manager.fields import MediaFKField
from .models import Popup


class PopupForm(forms.ModelForm):
    remove_file = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial='0'
    )
    # Single picker field — accepts both image and video
    # type filtering handled by data-type on the picker button in the template
    file_media = MediaFKField()

    class Meta:
        model  = Popup
        fields = ['title', 'start_date', 'end_date', 'type', 'link', 'status']
        widgets = {
            'title':      forms.TextInput(attrs={'placeholder': 'Popup title'}),
            'start_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'end_date':   forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'type':       forms.Select(
                attrs={'class': 'form-control', 'id': 'id_type'}
            ),
            'link':       forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': 'https://example.com or /page/'}
            ),
            'status':     forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end   = cleaned.get('end_date')
        if start and end and end < start:
            raise ValidationError("End date cannot be before start date.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('file_media')
        if media is not None:
            instance.file = media
        if commit:
            instance.save()
        return instance