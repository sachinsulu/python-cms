from rest_framework import serializers
from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage, SubPackageAmenity
from testimonials.models import Testimonial
from social.models import Social
from nearby.models import Nearby
from faq.models import FAQ
from menu.models import MenuItem
from features.models import Feature, FeatureGroup
from services.models import Service
from popup.models import Popup
from offers.models import Offer
from core.models import Module
from location.models import Location
from preferences.models import SitePreferences
from media_manager.models import Media, MediaFolder
from slideshow.models import Slideshow
from gallery.models import Gallery, GalleryImage


# Only the ArticleSerializer changes — rest of the file stays identical

class ArticleSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_alt = serializers.CharField(source='image.alt_text', read_only=True)
    image_title = serializers.CharField(source='image.title', read_only=True)

    class Meta:
        model = Article
        fields = ['title', 'content', 'image_url', 'image_alt', 'image_title']

    def get_image_url(self, obj):
        """
        Resolves image URL via the model property.
        Handles FK → legacy → None fallback automatically.
        Builds absolute URL when request context is available.
        """
        url = obj.image_url
        if not url:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'


class FeatureGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureGroup
        fields = ['id', 'title', 'active', 'position']


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'title', 'image', 'content', 'icon', 'active', 'position']


class SubPackageSerializer(serializers.ModelSerializer):
    amenities = serializers.SerializerMethodField()

    class Meta:
        model = SubPackage
        fields = [
            'id', 'title', 'slug', 'content', 'image',
            'price', 'capacity', 'beds', 'amenities',
            'is_active', 'position',
        ]

    def get_amenities(self, obj):
        # Use prefetched amenity_links to avoid extra queries.
        # Falls back gracefully if prefetch wasn't done.
        if hasattr(obj, '_prefetched_objects_cache') and 'amenity_links' in obj._prefetched_objects_cache:
            features = [
                link.feature for link in obj.amenity_links.all()
                if link.feature.active
            ]
        else:
            features = obj.amenities.filter(active=True).order_by('amenity_links__position')
        return FeatureSerializer(features, many=True, context=self.context).data


class PackageSerializer(serializers.ModelSerializer):
    sub_packages = SubPackageSerializer(many=True, read_only=True)
    feature_group = FeatureGroupSerializer(read_only=True)

    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'content', 'image',
            'package_type', 'feature_group',
            'is_active', 'position',
            'sub_packages',
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            'id', 'title', 'name', 'content', 'rating',
            'image', 'linksrc', 'country', 'via_type', 'position',
        ]


class SocialSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    image_url    = serializers.SerializerMethodField()

    class Meta:
        model  = Social
        fields = [
            'id', 'title', 'link',
            'image_url',          # resolved URL (FK or legacy)
            'icon', 'type', 'type_display', 'position',
        ]

    def get_image_url(self, obj):
        """
        Resolve image URL from FK (Media) or legacy ImageField.
        Builds an absolute URL when a request context is available.
        """
        url = obj.image_url  # model property handles FK vs legacy resolution
        if not url:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url


class NearbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nearby
        fields = ['id', 'title', 'distance', 'active', 'position']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'title', 'content', 'active', 'position']


class ChildMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'label', 'url', 'position', 'open_in_new_tab']


class MenuItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'label', 'url', 'open_in_new_tab', 'position', 'children']

    def get_children(self, instance):
        active_children = instance.children.filter(active=True).order_by('position')
        return ChildMenuItemSerializer(active_children, many=True).data

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'link', 'content', 'icon', 'status', 'position', 'type']

class PopupSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Popup
        fields = ['id', 'title', 'start_date', 'end_date', 'type', 'link', 'status', 'position', 'file_url']

    def get_file_url(self, obj):
        url = obj.file_url
        if not url:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'




class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Location
        fields = [
            'fiscal_address', 'ktm_address', 'ktm_contact_info',
            'ktm_email', 'landline', 'phone', 'p_o_box',
            'email_address', 'whatsapp', 'map_embed', 'content',
        ]

class SitePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitePreferences
        fields = '__all__'


class MediaSerializer(serializers.ModelSerializer):
    url = serializers.FileField(source='file', read_only=True)
    size_display = serializers.CharField(read_only=True)

    class Meta:
        model = Media
        fields = [
            'id', 'title', 'file', 'url', 'folder', 'type',
            'alt_text', 'size', 'size_display', 'width', 'height',
            'uploaded_by', 'created_at', 'position'
        ]


class MediaFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'parent', 'created_at']


class MediaFolderDetailSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    subfolders = MediaFolderSerializer(source='children', many=True, read_only=True)

    class Meta:
        model = MediaFolder
        fields = ['id', 'name', 'parent', 'created_at', 'media', 'subfolders']

    def get_media(self, obj):
        active_media = obj.media.active().order_by('position', '-created_at')
        return MediaSerializer(active_media, many=True, context=self.context).data


class SlideshowSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Slideshow
        fields = [
            'id', 'title', 'subtitle', 'type',
            'image_url', 'content', 'active', 'position',
        ]

    def get_image_url(self, obj):
        url = obj.image_url
        if not url:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

class GalleryImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = '__all__'

    def get_image_url(self, obj):
        if not obj.image_id:
            return None
        try:
            url = obj.image.file.url
            request = self.context.get('request')
            return request.build_absolute_uri(url) if request else url
        except (ValueError, AttributeError):
            return None

class GallerySerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = '__all__'
    def get_images(self, obj):
        # Try to use prefetched data if available
        if hasattr(obj, '_prefetched_objects_cache') and 'images' in obj._prefetched_objects_cache:
            images = obj.images.all()
        else:
            images = obj.images.filter(active=True).order_by('position')
        return GalleryImageSerializer(images, many=True, context=self.context).data

