from django import forms
from .models import Package


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['title', 'slug', 'description', 'image', 'package_type', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Package Title'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Package Description'
            }),
            'image': forms.FileInput(),
            'package_type': forms.RadioSelect(),
        }