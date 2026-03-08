from django.urls import path
from . import views

urlpatterns = [
    # Articles
    path('articles/', views.get_all_articles, name='get_all_articles'),
    path('articles/<slug:slug>/', views.get_article, name='get_article'),

    # Blogs
    path('blogs/', views.get_all_blogs, name='get_all_blogs'),
    path('blogs/<slug:slug>/', views.get_blog, name='get_blog'),

    # Packages
    path('packages/', views.get_all_packages, name='get_all_packages'),
    path('packages/<slug:slug>/', views.get_package, name='get_package'),

    # SubPackages
    path('sub/', views.get_all_subpackages, name='get_all_subpackages'),
    path('sub/<slug:slug>/', views.get_subpackage, name='get_subpackage'),

    # Testimonials
    path('testimonials/', views.get_all_testimonials, name='get_all_testimonials'),
    path('testimonials/<int:pk>/', views.get_testimonial, name='get_testimonial'),

    # Social & OTA
    path('social_list/', views.social_list, name='social_list'),
    path('social/', views.get_all_socials, name='get_all_socials'),
    path('ota/', views.get_all_otas, name='get_all_otas'),
    path('social/<int:pk>/', views.get_social, name='get_social'),


    # Nearby
    path('nearby/', views.get_all_nearby, name='get_all_nearby'),
    path('nearby/<int:pk>/', views.get_nearby, name='get_nearby'),
]