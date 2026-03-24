# blog/forms.py
from django import forms
from .models import Blog
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from media_manager.fields import MediaFKField


class BlogForm(forms.ModelForm):
    remove_image        = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial='0'
    )
    remove_banner_image = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial='0'
    )

    # Picker hidden fields
    image_media        = MediaFKField()
    banner_image_media = MediaFKField()

    slug = forms.CharField(
        required=False,
        help_text="URL-friendly version of the title. Edit if needed.",
        widget=forms.TextInput(attrs={"placeholder": "Slug"})
    )

    class Meta:
        model = Blog
        fields = [
            'title', 'slug', 'author', 'date',
            'content', 'active',
            'meta_title', 'meta_description', 'meta_keywords',
        ]
        # image and banner_image excluded — handled by picker fields
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'meta_description': forms.Textarea(attrs={
                'rows': 3, 'cols': 55,
                'placeholder': 'Meta Description',
            }),
            'meta_title':    forms.TextInput(attrs={'placeholder': 'Meta Title'}),
            'meta_keywords': forms.TextInput(attrs={'placeholder': 'Meta Keywords'}),
            'title':         forms.TextInput(attrs={'placeholder': 'Title'}),
            'author':        forms.TextInput(attrs={'placeholder': 'Author'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '').strip()
        if not slug:
            title = self.cleaned_data.get('title', '')
            slug  = slugify(title) if title else ''
        else:
            slug = slugify(slug)
        if not slug:
            raise ValidationError(
                "Slug cannot be empty. Please provide a title or slug."
            )
        from cms.utils import is_slug_taken
        exclude_obj = self.instance if self.instance.pk else None
        if is_slug_taken(slug, exclude_obj=exclude_obj):
            raise ValidationError(
                f"The slug '{slug}' is already in use. "
                "Please choose a different one."
            )
        return slug

    def clean(self):
        cleaned_data = super().clean()
        if 'slug' not in cleaned_data or not cleaned_data['slug']:
            title = cleaned_data.get('title')
            if title:
                cleaned_data['slug'] = slugify(title)
        return cleaned_data

    def clean_meta_title(self):
        meta_title = self.cleaned_data.get("meta_title", "").strip()
        if meta_title and len(meta_title) < 20:
            raise ValidationError(
                "Meta title must be at least 20 characters long."
            )
        return meta_title

    def save(self, commit=True):
        instance = super().save(commit=False)

        image        = self.cleaned_data.get('image_media')
        banner_image = self.cleaned_data.get('banner_image_media')

        if image is not None:
            instance.image = image
        if banner_image is not None:
            instance.banner_image = banner_image

        if commit:
            instance.save()
        return instance