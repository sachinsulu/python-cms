from django import forms
from .models import Nearby

class NearbyForm(forms.ModelForm):
    class Meta:
        model = Nearby
        fields = ['title', 'distance', 'map', 'content', 'active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter title'
            }),
            'distance': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 2.5 km'
            }),
            'map': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter map URL or embed code'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Title',
            'distance': 'Distance',
            'map': 'Map',
            'content': 'Content',
            'active': 'Active',
        }


    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 2:
                raise forms.ValidationError('Title must be at least 2 characters long.')
        return title

    def clean_distance(self):
        distance = self.cleaned_data.get('distance')
        if distance:
            distance = distance.strip()
            if not distance:
                raise forms.ValidationError('Distance cannot be blank.')
        return distance