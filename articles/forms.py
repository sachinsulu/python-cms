# articles/forms.py
from django import forms
from .models import Article
from django.utils.text import slugify
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.core.exceptions import ValidationError
from media_manager.fields import MediaFKField


class ArticleForm(forms.ModelForm):
    # Picker hidden field — JS writes Media.pk here on selection
    image_media = MediaFKField()

    slug = forms.CharField(
        required=False,
        help_text="URL-friendly version of the title. Edit if needed.",
        widget=forms.TextInput(attrs={"placeholder": "Slug"})
    )

    class Meta:
        model = Article
        # image is intentionally excluded from Meta.fields
        # it is handled entirely by image_media + form.save()
        fields = [
            'title', 'subtitle', 'slug', 'content',
            'active', 'meta_title', 'meta_description', 'meta_keywords',
        ]
        widgets = {
            'meta_description': forms.Textarea(attrs={
                'rows': 3,
                'cols': 55,
                'placeholder': 'Meta Descriptions',
            }),
            'meta_title':    forms.TextInput(attrs={'placeholder': 'Meta Title'}),
            'meta_keywords': forms.TextInput(attrs={'placeholder': 'Meta Keywords'}),
            'title':         forms.TextInput(attrs={'placeholder': 'Title'}),
            'subtitle':      forms.TextInput(attrs={'placeholder': 'Sub Title'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '').strip()

        if not slug:
            title = self.cleaned_data.get('title', '')
            slug = slugify(title) if title else ''
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

        media = self.cleaned_data.get('image_media')
        # Only overwrite if picker submitted a value.
        # If image_media is None it means the user did not touch the
        # image field at all — we preserve whatever FK is already set.
        if media is not None:
            instance.image = media

        if commit:
            instance.save()
        return instance