from rest_framework import serializers
from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage
from testimonials.models import Testimonial
from social.models import Social
from nearby.models import Nearby


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