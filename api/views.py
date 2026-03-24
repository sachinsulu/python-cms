from django.db.models import Prefetch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status



from package.models import Package, SubPackage, SubPackageAmenity
from articles.models import Article
from blog.models import Blog
from testimonials.models import Testimonial
from social.models import Social
from nearby.models import Nearby
from faq.models import FAQ
from menu.models import MenuItem
from features.models import Feature
from services.models import Service
from popup.models import Popup
from offers.models import Offer
from core.models import Module
from preferences.models import SitePreferences
from location.models import Location
from django.utils.text import slugify
from media_manager.models import Media, MediaFolder

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
    ServiceSerializer,
    PopupSerializer,
    OfferSerializer,
    ModuleSerializer,
    SitePreferenceSerializer,
    LocationSerializer,
    MediaSerializer,
    MediaFolderSerializer,
    MediaFolderDetailSerializer,
)


# ========================
# Article APIs
# ========================

@api_view(['GET'])
def get_article(request, slug):
    try:
        article = Article.objects.select_related('image').get(slug=slug, active=True)
    except Article.DoesNotExist:
        return Response(
            {'error': 'Article not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ArticleSerializer(article, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_all_articles(request):
    articles = Article.objects.filter(active=True).select_related('image')
    serializer = ArticleSerializer(articles, many=True, context={'request': request})
    return Response(serializer.data)



# ========================
# Blog APIs
# ========================

@api_view(['GET'])
def get_blog(request, slug):
    try:
        blog = Blog.objects.select_related('image', 'banner_image').get(slug=slug, active=True)
    except Blog.DoesNotExist:
        return Response(
            {'error': 'Blog not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = BlogSerializer(blog, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_all_blogs(request):
    blogs = Blog.objects.filter(active=True).select_related('image', 'banner_image')
    serializer = BlogSerializer(blogs, many=True, context={'request': request})
    return Response(serializer.data)


# ========================
# Package APIs
# ========================

@api_view(['GET'])
def get_all_packages(request):
    """Get all active packages with their sub-packages nested inside."""
    packages = Package.objects.filter(is_active=True).select_related('feature_group').prefetch_related(
        Prefetch(
            'sub_packages',
            queryset=SubPackage.objects.filter(is_active=True).prefetch_related(
                Prefetch(
                    'amenity_links',
                    queryset=SubPackageAmenity.objects.select_related('feature__image').order_by('position'),
                )
            )
        )
    ).order_by('position')
    serializer = PackageSerializer(packages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_package(request, slug):
    """Get a single package by slug with its sub-packages."""
    try:
        package = Package.objects.select_related('feature_group').prefetch_related(
            Prefetch(
                'sub_packages',
                queryset=SubPackage.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'amenity_links',
                        queryset=SubPackageAmenity.objects.select_related('feature__image').order_by('position'),
                    )
                )
            )
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
    testimonials = Testimonial.objects.filter(active=True).select_related('image').order_by('position')
    serializer = TestimonialSerializer(testimonials, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_testimonial(request, pk):
    """Get a single testimonial by id."""
    try:
        testimonial = Testimonial.objects.select_related('image').get(pk=pk, active=True)
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
    socials = Social.objects.filter(active=True).select_related('image').order_by('position')
    serializer = SocialSerializer(socials, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def get_all_socials(request):
    """Get all active social links ordered by position."""
    socials = Social.objects.filter(active=True, type=Social.TYPE_SOCIAL).select_related('image').order_by('position')
    serializer = SocialSerializer(socials, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_all_otas(request):
    """Get all active OTA links ordered by position."""
    otas = Social.objects.filter(active=True, type=Social.TYPE_OTA).select_related('image').order_by('position')
    serializer = SocialSerializer(otas, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_social(request, pk):
    """Get a single social or OTA entry by id."""
    try:
        item = Social.objects.select_related('image').get(pk=pk, active=True)
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
        package = Package.objects.select_related('feature_group').prefetch_related(
            Prefetch(
                'sub_packages',
                queryset=SubPackage.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'amenity_links',
                        queryset=SubPackageAmenity.objects.select_related('feature__image').order_by('position'),
                    )
                )
            )
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
    features = Feature.objects.filter(status=Feature.STATUS_ACTIVE).select_related('image').order_by('position')
    return Response(FeatureSerializer(features, many=True, context={'request': request}).data)

@api_view(['GET'])
def get_feature(request, pk):
    try:
        feature = Feature.objects.get(pk=pk, status=Feature.STATUS_ACTIVE)
    except Feature.DoesNotExist:
        return Response({'error': 'Feature not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(FeatureSerializer(feature, context={'request': request}).data)


# ========================
# Service APIs
# ========================

@api_view(['GET'])
def get_all_services(request):
    services = Service.objects.filter(active=True).order_by('position')
    return Response(ServiceSerializer(services, many=True, context={'request': request}).data)

@api_view(['GET'])
def get_service(request, pk):
    try:
        service = Service.objects.get(pk=pk, active=True)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ServiceSerializer(service, context={'request': request}).data)


# ========================
# Popup APIs
# ========================

@api_view(['GET'])
def get_all_popups(request):
    popups = Popup.objects.filter(active=True).order_by('position')
    return Response(PopupSerializer(popups, many=True, context={'request': request}).data)

@api_view(['GET'])
def get_popup(request, pk):
    try:
        popup = Popup.objects.get(pk=pk, active=True)
    except Popup.DoesNotExist:
        return Response({'error': 'Popup not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(PopupSerializer(popup, context={'request': request}).data)


# ========================
# Offer APIs
# ========================

@api_view(['GET'])
def get_all_offers(request):
    """Get all active offers ordered by position."""
    offers = Offer.objects.filter(active=True).order_by('position')
    serializer = OfferSerializer(offers, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_offer(request, pk):
    """Get a single offer by id."""
    try:
        offer = Offer.objects.get(pk=pk, active=True)
    except Offer.DoesNotExist:
        return Response(
            {'error': 'Offer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = OfferSerializer(offer, context={'request': request})
    return Response(serializer.data)


# ========================
# Core Module APIs
# ========================

@api_view(['GET'])
def get_all_modules(request):
    """Get all active core modules ordered by position."""
    modules = Module.objects.filter(is_active=True).order_by('order')
    serializer = ModuleSerializer(modules, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_module(request, pk):
    """Get a single core module by id."""
    try:
        module = Module.objects.get(pk=pk, is_active=True)
    except Module.DoesNotExist:
        return Response(
            {'error': 'Module not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ModuleSerializer(module, context={'request': request})
    return Response(serializer.data)


# ========================
# Location API
# ========================



@api_view(['GET'])
def get_location(request):
    location = Location.objects.get_solo()
    serializer = LocationSerializer(location, context={'request': request})
    return Response(serializer.data)


# ========================
# Site Preferences API
# ========================



@api_view(['GET'])
def get_site_preferences(request):
    preferences = SitePreferences.objects.get_solo()
    serializer = SitePreferenceSerializer(preferences, context={'request': request})
    return Response(serializer.data)


# ========================
# Media APIs
# ========================

@api_view(['GET'])
def get_all_media(request):
    """Get all active media files."""
    media = Media.objects.active().order_by('-created_at')
    
    # Filter by folder if provided
    folder_id = request.query_params.get('folder')
    if folder_id:
        media = media.filter(folder_id=folder_id)
        
    serializer = MediaSerializer(media, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_media(request, title):
    """Get a single media item by title."""
    try:
        media = Media.objects.active().get(title=title)
    except Media.DoesNotExist:
        return Response({'error': 'Media not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = MediaSerializer(media, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_all_media_folders(request):
    """Get all media folders."""
    folders = MediaFolder.objects.all().order_by('name')
    serializer = MediaFolderSerializer(folders, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_media_or_folder(request, name):
    """
    Dispatcher view that tries to find a media folder by name or slug first,
    then falls back to finding a single media item by title.
    """
    name = name.strip()
    # 1. Try to find a folder
    folder = MediaFolder.objects.filter(name__iexact=name).first()
    if not folder:
        # Fallback to slug match for folder
        for f in MediaFolder.objects.all():
            if slugify(f.name) == name:
                folder = f
                break
    
    if folder:
        serializer = MediaFolderDetailSerializer(folder, context={'request': request})
        return Response(serializer.data)

    # 2. If no folder, try to find a media item by title
    media = Media.objects.active().filter(title__iexact=name).first()
    if media:
        serializer = MediaSerializer(media, context={'request': request})
        return Response(serializer.data)

    # 3. Not found
    return Response(
        {'error': f"No folder or media item found with name '{name}'"}, 
        status=status.HTTP_404_NOT_FOUND
    )


@api_view(['GET'])
def get_media_folder_content(request, folder_name):
    """Legacy view, now handled by get_media_or_folder in common cases."""
    # ... existing implementation ...

