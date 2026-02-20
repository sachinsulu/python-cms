from django.db.models import Prefetch
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage
from .serializers import ArticleSerializer, BlogSerializer, PackageSerializer, SubPackageSerializer


@api_view(['GET'])
def get_article(request, slug):
    try:
        article = Article.objects.get(slug=slug, is_active=True)
    except Article.DoesNotExist:
        return Response(
            {'error': 'Article not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ArticleSerializer(article, context={'request': request})
    return Response(serializer.data)


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


@api_view(['GET'])
def get_all_articles(request):
    articles = Article.objects.filter(is_active=True, show_on_homepage=False)
    serializer = ArticleSerializer(articles, many=True, context={'request': request})
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

