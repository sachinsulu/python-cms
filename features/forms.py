# features/forms.py
from django import forms
from .models import Feature, FeatureGroup
from media_manager.fields import MediaFKField


class FeatureGroupForm(forms.ModelForm):
    class Meta:
        model  = FeatureGroup
        fields = ['title', 'active']
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Group title e.g., Room Amenities'}
            ),
        }


class FeatureForm(forms.ModelForm):
    remove_image = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial='0'
    )
    image_media = MediaFKField()

    class Meta:
        model  = Feature
        fields = ['title', 'content', 'icon', 'active']
        widgets = {
            'title':   forms.TextInput(attrs={'placeholder': 'Feature title'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description'}),
            'icon':    forms.TextInput(
                attrs={'placeholder': 'e.g. fa-solid fa-bolt'}
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