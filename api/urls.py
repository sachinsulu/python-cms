from django.urls import path
from . import views

urlpatterns = [
    # Articles
    path('articles/<slug:slug>/', views.get_article, name='get_article'),
    path('articles/', views.get_all_articles, name='get_all_articles'),

    # Blogs
    path('blogs/<slug:slug>/', views.get_blog, name='get_blog'),
    path('blogs/', views.get_all_blogs, name='get_all_blogs'),

    # Packages
    path('packages/', views.get_all_packages, name='get_all_packages'),
    path('packages/<slug:slug>/', views.get_package, name='get_package'),

    # SubPackages
    path('sub/', views.get_all_subpackages, name='get_all_subpackages'),
    path('sub/<slug:slug>/', views.get_subpackage, name='get_subpackage'),
]