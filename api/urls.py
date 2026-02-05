from django.urls import path
from . import views

urlpatterns = [
    # GET /api/articles/5/ -> returns article with id=5
    path('articles/<slug:slug>/', views.get_article, name='get_article'),
    path('blogs/<slug:slug>/', views.get_blog, name='get_blog'), 
    path('blogs/', views.get_all_blogs, name='get_all_blogs'),
    path('articles/', views.get_all_articles, name='get_all_articles'),
]