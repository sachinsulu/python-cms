# preferences/forms.py
from django import forms
from .models import SitePreferences
from media_manager.fields import MediaFKField  # ← correct import, no inline definition

IMAGE_FIELDS = [
    'icon', 'logo', 'fb_sharing', 'twitter_sharing',
    'gallery_image', 'contact_image', 'default_image',
    'facilities_image', 'offer_image',
]


class SitePreferencesForm(forms.ModelForm):

    icon_media             = MediaFKField()
    logo_media             = MediaFKField()
    fb_sharing_media       = MediaFKField()
    twitter_sharing_media  = MediaFKField()
    gallery_image_media    = MediaFKField()
    contact_image_media    = MediaFKField()
    default_image_media    = MediaFKField()
    facilities_image_media = MediaFKField()
    offer_image_media      = MediaFKField()

    class Meta:
        model  = SitePreferences
        fields = [
            'is_maintenance',
            'site_title', 'site_name', 'copyright_text',
            'google_analytics_code', 'facebook_pixel_code', 'online_booking_code',
            'robots_txt',
            'booking_type', 'hotel_result_page', 'hotel_code',
        ]
        widgets = {
            'site_title':            forms.TextInput(attrs={'placeholder': 'e.g. My Hotel | Official Site'}),
            'site_name':             forms.TextInput(attrs={'placeholder': 'e.g. My Hotel'}),
            'copyright_text':        forms.TextInput(attrs={'placeholder': 'e.g. © 2025 My Hotel. All rights reserved.'}),
            'google_analytics_code': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste full <script> tag here'}),
            'facebook_pixel_code':   forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste full <script> tag here'}),
            'online_booking_code':   forms.Textarea(attrs={'rows': 5, 'placeholder': 'Paste booking widget embed code here'}),
            'robots_txt':            forms.Textarea(attrs={'rows': 6, 'placeholder': 'User-agent: *\nAllow: /'}),
            'hotel_result_page':     forms.TextInput(attrs={'placeholder': 'e.g. /booking/results/'}),
            'hotel_code':            forms.TextInput(attrs={'placeholder': 'e.g. HTL-001'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        for field in IMAGE_FIELDS:
            media_obj = self.cleaned_data.get(f'{field}_media')
            if media_obj is not None:
                setattr(instance, field, media_obj)
        if commit:
            instance.save()
        return instance