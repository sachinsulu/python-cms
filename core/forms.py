from django import forms
from .models import Module

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['label', 'icon', 'url_name', 'url_name_match', 'permission_app', 'superuser_only', 'is_active', 'order']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-solid fa-newspaper'}),
            'url_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'article_list'}),
            'url_name_match': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'article,article_create'}),
            'permission_app': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'blog'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }