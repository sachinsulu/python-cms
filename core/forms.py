from django import forms
from .models import Module, PageMeta
from django.core.exceptions import ValidationError


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

class PageMetaForm(forms.ModelForm):
    class Meta:
        model = PageMeta
        fields = ['meta_title', 'meta_description', 'meta_keywords']
        widgets = {
            'meta_title': forms.TextInput(attrs={
                'placeholder': 'Meta title (max 60 chars)',
                'id': 'id_meta_title',
            }),
            'meta_description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Meta description (max 160 chars)',
                'id': 'id_meta_description',
            }),
            'meta_keywords': forms.TextInput(attrs={
                'placeholder': 'keyword1, keyword2, keyword3',
                'id': 'id_meta_keywords',
            }),
        }

    def clean_meta_title(self):
        value = self.cleaned_data.get('meta_title', '').strip()
        if value and len(value) < 20:
            raise ValidationError(
                'Meta title should be at least 20 characters long.'
            )
        return value