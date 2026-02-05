from rest_framework import serializers
from articles.models import Article
from blog.models import Blog


class ArticleSerializer(serializers.ModelSerializer):
    """
    This converts an Article object into JSON format.
    We only include the fields we need.
    """
    
    class Meta:
        model = Article
        fields = [
            'title',
            'content',
            'image',
            
        ]
    



class BlogSerializer(serializers.ModelSerializer):
    """
    This converts a Blog object into JSON format.
    We only include the fields we need.
    """
    class Meta:
        model = Blog
        fields = [
            'title',
            'subtitle',
            'content',
        ]
