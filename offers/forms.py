# offers/forms.py
from django import forms
from django.core.exceptions import ValidationError
from media_manager.fields import MediaFKField
from .models import Offer


class OfferForm(forms.ModelForm):
    remove_image = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial='0'
    )
    image_media = MediaFKField()

    class Meta:
        model  = Offer
        fields = [
            'title', 'start_date', 'end_date',
            'discount_type',
            'fixed_discount', 'fixed_rate', 'fixed_people',
            'link', 'content', 'active',
        ]
        widgets = {
            'title':          forms.TextInput(attrs={'placeholder': 'Offer title'}),
            'start_date':     forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'end_date':       forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'discount_type':  forms.Select(attrs={'id': 'id_discount_type'}),
            'fixed_discount': forms.NumberInput(
                attrs={'placeholder': 'Discount amount', 'step': '0.01'}
            ),
            'fixed_rate':     forms.NumberInput(
                attrs={'placeholder': 'Rate', 'step': '0.01'}
            ),
            'fixed_people':   forms.NumberInput(
                attrs={'placeholder': 'No. of people'}
            ),
            'link':           forms.TextInput(
                attrs={'placeholder': 'https://example.com or /page/'}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end   = cleaned.get('end_date')
        if start and end and end < start:
            raise ValidationError('End date cannot be before start date.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('image_media')
        if media is not None:
            instance.image = media
        if commit:
            instance.save()
        return instance