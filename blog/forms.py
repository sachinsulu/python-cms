from django import forms
from .models import Blog
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title','slug', 'subtitle', 'content','homepage','active']
        widgets = {
            # This keeps the field in the form but hides it from the user's eyes
            'homepage': forms.HiddenInput(),
        }





    def clean_slug(self):
        """Validate and clean the slug field"""
        # Get the slug value directly from the form field
        slug = self.cleaned_data.get('slug', '').strip()
        
        # If slug field is empty, generate from title
        if not slug:
            title = self.cleaned_data.get('title', '')
            slug = slugify(title) if title else ''
        else:
            # If user provided a slug, ensure it's properly slugified
            slug = slugify(slug)
        
        if not slug:
            raise ValidationError("Slug cannot be empty. Please provide a title or slug.")
        
        # Cross-model slug uniqueness check
        from cms.utils import is_slug_taken
        exclude_obj = self.instance if self.instance.pk else None
        if is_slug_taken(slug, exclude_obj=exclude_obj):
            raise ValidationError(
                f"The slug '{slug}' is already in use. Please choose a different one."
            )
        
        return slug

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure slug is set (in case clean_slug wasn't called due to other errors)
        if 'slug' not in cleaned_data or not cleaned_data['slug']:
            title = cleaned_data.get('title')
            if title:
                cleaned_data['slug'] = slugify(title)
        
        return cleaned_data