from django import forms
from .models import Feature, FeatureGroup

class FeatureGroupForm(forms.ModelForm):
    class Meta:
        model = FeatureGroup
        fields = ['title', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Group title e.g., Room Amenities'}),
        }

class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ['title', 'image', 'content', 'icon', 'active']  # group removed
        widgets = {
            'title':   forms.TextInput(attrs={'placeholder': 'Feature title'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description'}),
            'icon':    forms.TextInput(attrs={'placeholder': 'e.g. fa-solid fa-bolt'}),
            'image':   forms.FileInput(),
        }