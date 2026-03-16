from django.db.models import Prefetch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage
from testimonials.models import Testimonial
from social.models import Social
from nearby.models import Nearby
from faq.models import FAQ
from menu.models import MenuItem
from features.models import Feature

from .serializers import (
    ArticleSerializer,
    BlogSerializer,
    PackageSerializer,
    SubPackageSerializer,
    TestimonialSerializer,
    SocialSerializer,
    NearbySerializer,
    FAQSerializer,
    MenuItemSerializer,
    FeatureSerializer,
)


# ========================
# Article APIs
# ========================

@api_view(['GET'])
def get_article(request, slug):
    try:
        article = Article.objects.get(slug=slug, active=True)
    except Article.DoesNotExist:
        return Response(
            {'error': 'Article not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ArticleSerializer(article, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_all_articles(request):
    articles = Article.objects.filter(active=True)
    serializer = ArticleSerializer(articles, many=True, context={'request': request})
    return Response(serializer.data)


# ========================
# Blog APIs
# ========================

@api_view(['GET'])
def get_blog(request, slug):
    try:
        blog = Blog.objects.get(slug=slug, active=True)
    except Blog.DoesNotExist:
        return Response(
            {'error': 'Blog not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = BlogSerializer(blog, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_all_blogs(request):
    blogs = Blog.objects.filter(active=True)
    serializer = BlogSerializer(blogs, many=True, context={'request': request})
    return Response(serializer.data)


# ========================
# Package APIs
# ========================

@api_view(['GET'])
def get_all_packages(request):
    """Get all active packages with their sub-packages nested inside."""
    packages = Package.objects.filter(is_active=True).prefetch_related(
        Prefetch('sub_packages', queryset=SubPackage.objects.filter(is_active=True))
    ).order_by('position')
    serializer = PackageSerializer(packages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_package(request, slug):
    """Get a single package by slug with its sub-packages."""
    try:
        package = Package.objects.prefetch_related(
            Prefetch('sub_packages', queryset=SubPackage.objects.filter(is_active=True))
        ).get(slug=slug, is_active=True)
    except Package.DoesNotExist:
        return Response(
            {'error': 'Package not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = PackageSerializer(package, context={'request': request})
    return Response(serializer.data)


# ========================
# SubPackage APIs
# ========================

@api_view(['GET'])
def get_all_subpackages(request):
    """Get all active sub-packages across all packages."""
    subpackages = SubPackage.objects.filter(
        is_active=True,
        package__is_active=True
    ).order_by('package__position', 'position')
    serializer = SubPackageSerializer(subpackages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_subpackage(request, slug):
    """Get a single sub-package by slug."""
    try:
        sub = SubPackage.objects.get(slug=slug, is_active=True, package__is_active=True)
    except SubPackage.DoesNotExist:
        return Response(
            {'error': 'Sub-package not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = SubPackageSerializer(sub, context={'request': request})
    return Response(serializer.data)


# ========================
# Testimonial APIs
# ========================

@api_view(['GET'])
def get_all_testimonials(request):
    """Get all active testimonials ordered by position."""
    testimonials = Testimonial.objects.filter(active=True).order_by('position')
    serializer = TestimonialSerializer(testimonials, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_testimonial(request, pk):
    """Get a single testimonial by id."""
    try:
        testimonial = Testimonial.objects.get(pk=pk, active=True)
    except Testimonial.DoesNotExist:
        return Response(
            {'error': 'Testimonial not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = TestimonialSerializer(testimonial, context={'request': request})
    return Response(serializer.data)


# ========================
# Social / OTA APIs
# ========================

@api_view(['GET'])
def social_list(request):
    """Get all active social links ordered by position."""
    socials = Social.objects.filter(active=True).order_by('position')
    serializer = SocialSerializer(socials, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def get_all_socials(request):
    """Get all active social links ordered by position."""
    socials = Social.objects.filter(active=True, type=Social.TYPE_SOCIAL).order_by('position')
    serializer = SocialSerializer(socials, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_all_otas(request):
    """Get all active OTA links ordered by position."""
    otas = Social.objects.filter(active=True, type=Social.TYPE_OTA).order_by('position')
    serializer = SocialSerializer(otas, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_social(request, pk):
    """Get a single social or OTA entry by id."""
    try:
        item = Social.objects.get(pk=pk, active=True)
    except Social.DoesNotExist:
        return Response(
            {'error': 'Not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = SocialSerializer(item, context={'request': request})
    return Response(serializer.data)


# ========================
# Nearby APIs
# ========================

@api_view(['GET'])
def get_all_nearby(request):
    """Get all active nearby places ordered by position."""
    nearby_places = Nearby.objects.filter(active=True).order_by('position')
    serializer = NearbySerializer(nearby_places, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_nearby(request, pk):
    """Get a single nearby place by id."""
    try:
        nearby = Nearby.objects.get(pk=pk, active=True)
    except Nearby.DoesNotExist:
        return Response(
            {'error': 'Nearby place not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = NearbySerializer(nearby, context={'request': request})
    return Response(serializer.data)


# ========================
# FAQ APIs
# ========================

@api_view(['GET'])
def get_all_faqs(request):
    """Get all active FAQs ordered by position."""
    faqs = FAQ.objects.filter(active=True).order_by('position')
    serializer = FAQSerializer(faqs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_faq(request, pk):
    """Get a single FAQ by id."""
    try:
        faq = FAQ.objects.get(pk=pk, active=True)
    except FAQ.DoesNotExist:
        return Response(
            {'error': 'FAQ not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = FAQSerializer(faq, context={'request': request})
    return Response(serializer.data)




# ========================
# Menu API
# ========================

@api_view(['GET'])
def get_menu(request):
    items = (
        MenuItem.objects
        .filter(active=True, parent=None)
        .prefetch_related('children')
        .order_by('position')
    )
    serializer = MenuItemSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


# ========================
# Universal Slug API
# ========================

@api_view(['GET'])
def get_by_slug(request, slug):
    """
    Looks up a given slug across Article, Blog, Package, and SubPackage.
    Returns the first matching active item along with its type.
    """
    
    # Check Articles
    try:
        article = Article.objects.get(slug=slug, active=True)
        serializer = ArticleSerializer(article, context={'request': request})
        return Response({
            'type': 'article',
            'data': serializer.data
        })
    except Article.DoesNotExist:
        pass

    # Check Blogs
    try:
        blog = Blog.objects.get(slug=slug, active=True)
        serializer = BlogSerializer(blog, context={'request': request})
        return Response({
            'type': 'blog',
            'data': serializer.data
        })
    except Blog.DoesNotExist:
        pass

    # Check Packages
    try:
        package = Package.objects.prefetch_related(
            Prefetch('sub_packages', queryset=SubPackage.objects.filter(is_active=True))
        ).get(slug=slug, is_active=True)
        serializer = PackageSerializer(package, context={'request': request})
        return Response({
            'type': 'package',
            'data': serializer.data
        })
    except Package.DoesNotExist:
        pass

    # Check SubPackages
    try:
        sub = SubPackage.objects.get(slug=slug, is_active=True, package__is_active=True)
        serializer = SubPackageSerializer(sub, context={'request': request})
        return Response({
            'type': 'subpackage',
            'data': serializer.data
        })
    except SubPackage.DoesNotExist:
        pass

    # Nothing found
    return Response(
        {'error': 'Content not found for this slug.'},
        status=status.HTTP_404_NOT_FOUND
    )



# ========================
# Feature APIs
# ========================

@api_view(['GET'])
def get_all_features(request):
    features = Feature.objects.filter(status=Feature.STATUS_ACTIVE).order_by('position')
    return Response(FeatureSerializer(features, many=True, context={'request': request}).data)

@api_view(['GET'])
def get_feature(request, pk):
    try:
        feature = Feature.objects.get(pk=pk, status=Feature.STATUS_ACTIVE)
    except Feature.DoesNotExist:
        return Response({'error': 'Feature not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(FeatureSerializer(feature, context={'request': request}).data)