from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser 

from articles.models import Article 
from blog.models import Blog    
from .serializers import ArticleSerializer, BlogSerializer

@permission_classes([IsAdminUser])
@api_view(['GET'])
def get_article(request, slug):
    """
    Get a single article by its ID.
    
    How it works:
    1. Receives article_id from the URL
    2. Tries to find that article in the database
    3. Converts it to JSON using the serializer
    4. Sends it back
    """
    
    try:
        # Try to find the article with this ID
        article = Article.objects.get(slug=slug, is_active=True)
        
    except Article.DoesNotExist:
        # If article doesn't exist, return error
        return Response(
            {'error': 'Article not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Convert the article to JSON
    serializer = ArticleSerializer(article)
    
    # Send the JSON response
    return Response(serializer.data)

@permission_classes([IsAdminUser])
@api_view(['GET'])
def get_blog(request, slug):
    """
    Get a single article by its ID.
    
    How it works:
    1. Receives article_id from the URL
    2. Tries to find that article in the database
    3. Converts it to JSON using the serializer
    4. Sends it back
    """
    
    try:
        # Try to find the article with this ID
        blog = Blog.objects.get(slug=slug, active=True)
        
    except Blog.DoesNotExist:
        # If article doesn't exist, return error
        return Response(
            {'error': 'Blog not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Convert the article to JSON
    serializer = BlogSerializer(blog)
    
    # Send the JSON response
    return Response(serializer.data)

@permission_classes([IsAdminUser])
@api_view(['GET'])
def get_all_blogs(request):
    """
    Get a list of all active blogs.
    
    Returns all blogs that are active=True
    """
    # Get all active blogs
    blogs = Blog.objects.filter(active=True)
    
    # Convert to JSON (many=True for multiple objects)
    serializer = BlogSerializer(blogs, many=True)
    
    # Send the response
    return Response(serializer.data)


@permission_classes([IsAdminUser])
@api_view(['GET'])
def get_all_articles(request):
    """
    Get a list of all active articles.
    
    Returns all articles that are is_active=True
    """
    # Get all active articles
    articles = Article.objects.filter(is_active=True)
    
    # Convert to JSON (many=True for multiple objects)
    serializer = ArticleSerializer(articles, many=True, context={'request': request})
    
    # Send the response
    return Response(serializer.data)
    