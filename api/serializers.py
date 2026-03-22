from rest_framework import serializers
from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage
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


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image']


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
            'id', 'title', 'slug', 'description', 'image',
            'price', 'capacity', 'beds', 'amenities',
            'is_active', 'position',
        ]

    def get_amenities(self, obj):
        features = obj.amenities.filter(active=True).order_by('amenity_links__position')
        return FeatureSerializer(features, many=True, context=self.context).data


class PackageSerializer(serializers.ModelSerializer):
    sub_packages = SubPackageSerializer(many=True, read_only=True)
    feature_group = FeatureGroupSerializer(read_only=True)

    class Meta:
        model = Package
        fields = [
            'id', 'title', 'slug', 'description', 'image',
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

    class Meta:
        model = Social
        fields = ['id', 'title', 'link', 'image', 'icon', 'type', 'type_display', 'position']


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
        fields = ['id', 'title', 'content', 'image', 'icon', 'active', 'position']

class PopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Popup
        fields = ['id', 'title', 'content', 'image', 'icon', 'active', 'position']

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'


from location.models import Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Location
        fields = [
            'fiscal_address', 'ktm_address', 'ktm_contact_info',
            'ktm_email', 'landline', 'phone', 'p_o_box',
            'email_address', 'whatsapp', 'map_embed', 'content',
        ]