# services/forms.py
from django import forms
from .models import Service
from media_manager.fields import MediaFKField


class ServiceForm(forms.ModelForm):
    remove_image = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial='0'
    )
    image_media = MediaFKField()

    class Meta:
        model  = Service
        fields = ['title', 'link', 'content', 'icon', 'status']
        widgets = {
            'title':   forms.TextInput(attrs={'placeholder': 'Title'}),
            'link':    forms.TextInput(attrs={'placeholder': 'https://'}),
            'icon':    forms.TextInput(
                attrs={'placeholder': 'e.g. fa-brands fa-instagram'}
            ),
            'content': forms.Textarea(attrs={'rows': 4}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('image_media')
        if media is not None:
            instance.image = media
        if commit:
            instance.save()
        return instance