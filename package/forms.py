from django import forms
from django.core.exceptions import ValidationError
from features.models import FeatureGroup, Feature
from .models import Package, SubPackage, SubPackageImage
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from media_manager.fields import MediaFKField


class FeatureTitleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class PackageForm(forms.ModelForm):
    image_media = MediaFKField()

    class Meta:
        model = Package
        fields = [
            'title', 'slug', 'content',
            'package_type', 'feature_group', 'is_active',
            'meta_title', 'meta_description', 'meta_keywords',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Package Title'}),
            'content': CKEditorUploadingWidget(),
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('image_media')
        if media is not None:
            instance.image = media
        if commit:
            instance.save()
        return instance


class SubPackageForm(forms.ModelForm):
    image_media = MediaFKField()

    # Standalone field — not bound to the model, used only to render checkboxes
    amenities = FeatureTitleChoiceField(
        queryset=Feature.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    class Meta:
        model = SubPackage
        fields = [
            'title', 'slug', 'content',
            'price', 'capacity', 'beds',
            'hall_size', 'u_shape', 'classroom', 'theatre', 'round_table',
            'is_active',
            'meta_title', 'meta_description', 'meta_keywords',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Sub-Package Title'}),
            'content': CKEditorUploadingWidget(),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Max guests'}),
            'beds': forms.NumberInput(attrs={'placeholder': 'Number of beds'}),
            'hall_size': forms.TextInput(attrs={'placeholder': 'e.g. 2200 sq. ft'}),
            'u_shape': forms.TextInput(attrs={'placeholder': 'e.g. 60 pax'}),
            'classroom': forms.TextInput(attrs={'placeholder': 'e.g. 150 pax'}),
            'theatre': forms.TextInput(attrs={'placeholder': 'e.g. 250 chairs'}),
            'round_table': forms.TextInput(attrs={'placeholder': 'e.g. 90 pax'}),
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
        if self.instance and self.instance.pk:
            self.fields['amenities'].initial = self.instance.amenities.values_list('pk', flat=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        media = self.cleaned_data.get('image_media')
        if media is not None:
            instance.image = media
        if commit:
            instance.save()
        return instance


class SubPackageImageForm(forms.ModelForm):
    image_media = MediaFKField()

    class Meta:
        model = SubPackageImage
        fields = ['title', 'active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter image title (optional)'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }