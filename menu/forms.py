from django import forms
from .models import MenuItem


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['label', 'url', 'parent', 'open_in_new_tab', 'active']
        widgets = {
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. About Us',
            }),
            'url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. /about/ or https://example.com',
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control',
            }),
            'open_in_new_tab': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'label': 'Menu Label',
            'url': 'URL / Link',
            'parent': 'Parent Item (for dropdowns)',
            'open_in_new_tab': 'Open in New Tab',
            'active': 'Active',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only top-level items can be parents (no nesting beyond 1 level)
        self.fields['parent'].queryset = MenuItem.objects.filter(parent=None)
        self.fields['parent'].empty_label = "— Top Level (no parent) —"

        # If editing, exclude self from parent choices to prevent circular references
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = (
                MenuItem.objects
                .filter(parent=None)
                .exclude(pk=self.instance.pk)
            )

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        label = cleaned_data.get('label', '').strip()

        if not label:
            raise forms.ValidationError("Label cannot be empty.")

        # Prevent a child item from being set as a parent
        if parent and parent.parent is not None:
            raise forms.ValidationError(
                f"'{parent.label}' is already a child item and cannot be used as a parent. "
                "Only top-level items can have children."
            )

        return cleaned_data