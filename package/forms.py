from django import forms
from .models import Package, SubPackage


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


class SubPackageForm(forms.ModelForm):
    class Meta:
        model = SubPackage
        fields = [
            'title', 'slug', 'description', 'image',
            'price', 'capacity', 'beds', 'amenities',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Sub-Package Title'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Description'
            }),
            'image': forms.FileInput(),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Max guests'}),
            'beds': forms.NumberInput(attrs={'placeholder': 'Number of beds'}),
            'amenities': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'AC, WiFi, Mini Bar, TV'
            }),
        }