from django import forms
from features.models import FeatureGroup, Feature
from .models import Package, SubPackage
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class FeatureTitleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['title', 'slug', 'description', 'image', 'package_type', 'feature_group', 'is_active', 'meta_title', 'meta_description', 'meta_keywords']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Package Title'}),
            'description': CKEditorUploadingWidget(),
            'image': forms.FileInput(),
            'package_type': forms.RadioSelect(),
            'feature_group': forms.Select(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'placeholder': 'Meta title (max 60 chars)', 'maxlength': '60'}),
            'meta_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Meta description (max 160 chars)', 'maxlength': '160'}),
            'meta_keywords': forms.TextInput(attrs={'placeholder': 'Meta keywords (max 250 chars)', 'maxlength': '250'}),
        }
        labels = {
            'feature_group': 'Feature Group (Amenities Source)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feature_group'].queryset = FeatureGroup.objects.filter(active=True).order_by('position')
        self.fields['feature_group'].empty_label = '— No feature group —'


class SubPackageForm(forms.ModelForm):
    """
    amenities is excluded — handled manually in the view
    so we can persist the drag-and-drop position via SubPackageAmenity.
    """
    # Standalone field — not bound to the model, used only to render checkboxes
    amenities = FeatureTitleChoiceField(
        queryset=Feature.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    class Meta:
        model = SubPackage
        # amenities intentionally excluded from Meta.fields
        fields = ['title', 'slug', 'description', 'image', 'price', 'capacity', 'beds', 'is_active', 'meta_title', 'meta_description', 'meta_keywords']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Sub-Package Title'}),
            'description': CKEditorUploadingWidget(),
            'image': forms.FileInput(),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Max guests'}),
            'beds': forms.NumberInput(attrs={'placeholder': 'Number of beds'}),
            'meta_title': forms.TextInput(attrs={'placeholder': 'Meta title (max 60 chars)', 'maxlength': '60'}),
            'meta_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Meta description (max 160 chars)', 'maxlength': '160'}),
            'meta_keywords': forms.TextInput(attrs={'placeholder': 'Meta keywords (max 250 chars)', 'maxlength': '250'}),
        }

    def __init__(self, *args, feature_group=None, **kwargs):
        super().__init__(*args, **kwargs)
        if feature_group is not None:
            self.fields['amenities'].queryset = Feature.objects.filter(
                group=feature_group, active=True
            ).order_by('position')
        # Pre-select existing amenities when editing
        if self.instance and self.instance.pk:
            self.fields['amenities'].initial = self.instance.amenities.values_list('pk', flat=True)