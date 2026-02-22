from django import forms
from .models import Article
from django.utils.text import slugify
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image as PILImage


class ArticleForm(forms.ModelForm):
    # Hidden field for image removal
    remove_image = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    
    slug = forms.CharField(
        required=False,
        help_text="URL-friendly version of the title. Edit if needed.",
        widget=forms.TextInput(attrs={"placeholder": "Slug"})
    )

    class Meta:
        model = Article
        fields = [
            'title', 'subtitle', 'slug', 'image', 'content',
            'active', 'meta_title', 'meta_description', 'meta_keywords'
        ] 
        widgets = {
            'image': forms.FileInput(),
            'meta_description': forms.Textarea(attrs={
                'rows': 3,
                'cols': 55,
                'placeholder': 'Meta Descriptions'
            }),
            'meta_title': forms.TextInput(attrs={'placeholder': 'Meta Title'}),
            'meta_keywords': forms.TextInput(attrs={'placeholder': 'Meta Keywords'}),
            'title': forms.TextInput(attrs={'placeholder': 'Title'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'Sub Title'}),
        }

    def clean_image(self):
        """Validate uploaded image file"""
        image = self.cleaned_data.get('image')
        
        # If no image in cleaned_data, return None
        if not image:
            return image
        
        # If editing and keeping the same image (not a new upload)
        if self.instance and self.instance.pk and self.instance.image:
            if image == self.instance.image:
                return image
        
        # Only validate NEW file uploads (has 'file' attribute)
        if not hasattr(image, 'file'):
            return image
        
        # Get validation settings
        max_size = getattr(settings, 'IMAGE_MAX_FILE_SIZE', 2 * 1024 * 1024)
        allowed_extensions = getattr(settings, 'IMAGE_ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'webp','heic'])
        max_dimensions = getattr(settings, 'IMAGE_MAX_DIMENSIONS', (1920, 1280))
        allowed_mimetypes = getattr(settings, 'IMAGE_ALLOWED_MIMETYPES', [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp','image/heic'
        ])
        
        # 1. File size check
        if image.size > max_size:
            raise ValidationError(
                f"Image file too large. Maximum size is {max_size/(1024*1024):.0f}MB. "
                f"Your file is {image.size / (1024*1024):.1f}MB"
            )
        
        # 2. File extension check
        file_extension = image.name.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f"Invalid file type '.{file_extension}'. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # 3. Verify it's actually a valid image file
        try:
            img = PILImage.open(image)
            img.verify()
            image.seek(0)
        except Exception:
            raise ValidationError(
                "Invalid image file. The file may be corrupted or not a real image."
            )
        
        # 4. Check image dimensions
        try:
            img = PILImage.open(image)
            width, height = img.size
            
            max_width, max_height = max_dimensions
            if width > max_width or height > max_height:
                raise ValidationError(
                    f"Image dimensions too large. Maximum is {max_width}x{max_height}px. "
                    f"Your image is {width}x{height}px"
                )
            
            image.seek(0)
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError("Could not read image dimensions")
        
        # 5. MIME type check
        if hasattr(image, 'content_type'):
            if image.content_type not in allowed_mimetypes:
                raise ValidationError(
                    f"Invalid image format '{image.content_type}'. Allowed: JPEG, PNG, GIF, WebP , HEIC"
                )
        
        return image

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
        
        # Check for duplicate slugs in database
        qs = Article.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # If the 'X' was clicked in JS, this value will be '1'
        if self.cleaned_data.get('remove_image') == '1':
            instance.image = None
            
        if commit:
            instance.save()
        return instance
    
    def clean_meta_title(self):
        meta_title = self.cleaned_data.get("meta_title", "").strip()

        if meta_title and len(meta_title) < 20:
            raise ValidationError(
                "Meta title must be at least 20 characters long."
            )

        return meta_title