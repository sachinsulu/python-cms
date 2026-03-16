from rest_framework import serializers
from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage
from testimonials.models import Testimonial
from social.models import Social
from nearby.models import Nearby
from faq.models import FAQ
from menu.models import MenuItem
from features.models import Feature


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'title',
            'content',
            'image',
        ]


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            'title',
            'subtitle',
            'content',
        ]


class SubPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubPackage
        fields = [
            'title',
            'slug',
            'description',
            'image',
            'price',
            'capacity',
            'beds',
            'amenities',
            'is_active',
            'position',
        ]


class PackageSerializer(serializers.ModelSerializer):
    sub_packages = SubPackageSerializer(many=True, read_only=True)
    package_type_display = serializers.CharField(source='get_package_type_display', read_only=True)

    class Meta:
        model = Package
        fields = [
            'title',
            'slug',
            'description',
            'image',
            'package_type',
            'package_type_display',
            'is_active',
            'position',
            'sub_packages',
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            'id',
            'title',
            'name',
            'content',
            'rating',
            'image',
            'linksrc',
            'country',
            'via_type',
            'position',
        ]


class SocialSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Social
        fields = [
            'id',
            'title',
            'link',
            'image',
            'icon',
            'type',
            'type_display',
            'position',
        ]


class NearbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nearby
        fields = [
            'id',
            'title',
            'distance',
            'active',
            'position',
        ]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            'id',
            'title',
            'content',
            'active',
            'position',
        ]






class ChildMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'label', 'url','position', 'open_in_new_tab']


class MenuItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'label', 'url', 'open_in_new_tab', 'position', 'children']

    def get_children(self, instance):
        active_children = instance.children.filter(active=True).order_by('position')
        return ChildMenuItemSerializer(active_children, many=True).data




class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'title', 'image', 'content', 'icon', 'status', 'position']