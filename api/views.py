from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from articles.models import Article 
from blog.models import Blog    
from .serializers import ArticleSerializer, BlogSerializer


@api_view(['GET'])  # ✅ This decorator goes FIRST
@permission_classes([IsAdminUser])  # ✅ This goes SECOND
def get_article(request, slug):
    """
    Get a single article by its slug.
    Only accessible by admin users.
    """
    try:
        article = Article.objects.get(slug=slug, is_active=True)
    except Article.DoesNotExist:
        return Response(
            {'error': 'Article not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ArticleSerializer(article, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])  # ✅ First
@permission_classes([IsAdminUser])  # ✅ Second
def get_blog(request, slug):
    """
    Get a single blog by its slug.
    Only accessible by admin users.
    """
    try:
        blog = Blog.objects.get(slug=slug, active=True)
    except Blog.DoesNotExist:
        return Response(
            {'error': 'Blog not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = BlogSerializer(blog, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])  # ✅ First
@permission_classes([IsAdminUser])  # ✅ Second
def get_all_blogs(request):
    """
    Get a list of all active blogs.
    Only accessible by admin users.
    """
    blogs = Blog.objects.filter(active=True)
    serializer = BlogSerializer(blogs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])  # ✅ First
@permission_classes([IsAdminUser])  # ✅ Second
def get_all_articles(request):
    """
    Get a list of all active articles.
    Only accessible by admin users.
    """
    articles = Article.objects.filter(is_active=True)
    serializer = ArticleSerializer(articles, many=True, context={'request': request})
    return Response(serializer.data)