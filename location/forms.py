from django import forms
from .models import Location


class LocationForm(forms.ModelForm):
    class Meta:
        model  = Location
        fields = [
            'fiscal_address', 'ktm_address', 'ktm_contact_info',
            'ktm_email', 'landline', 'phone', 'p_o_box',
            'email_address', 'whatsapp', 'map_embed', 'content',
        ]
        widgets = {
            'fiscal_address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Full fiscal / registered address',
            }),
            'ktm_address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Kathmandu office address',
            }),
            'ktm_contact_info': forms.TextInput(attrs={
                'placeholder': 'e.g. +977-1-XXXXXXX',
            }),
            'ktm_email': forms.EmailInput(attrs={
                'placeholder': 'ktm@example.com',
            }),
            'landline': forms.TextInput(attrs={
                'placeholder': 'e.g. +977-1-XXXXXXX',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'e.g. +977-98XXXXXXXX',
            }),
            'p_o_box': forms.TextInput(attrs={
                'placeholder': 'e.g. P.O. Box 1234',
            }),
            'email_address': forms.EmailInput(attrs={
                'placeholder': 'info@example.com',
            }),
            'whatsapp': forms.TextInput(attrs={
                'placeholder': 'e.g. +977-98XXXXXXXX',
            }),
            'map_embed': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Paste Google Maps <iframe> embed code or a plain map URL',
            }),
        }
