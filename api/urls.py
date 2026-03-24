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

    # FAQ
    path('faq/', views.get_all_faqs, name='get_all_faqs'),
    path('faq/<int:pk>/', views.get_faq, name='get_faq'),


    # Menu
    path('menu/', views.get_menu, name='get_menu'),

    # Features
    path('features/', views.get_all_features, name='get_all_features'),
    path('features/<int:pk>/', views.get_feature, name='get_feature'),

    # Services
    path('services/', views.get_all_services, name='get_all_services'),
    path('services/<int:pk>/', views.get_service, name='get_service'),

    # Popups
    path('popups/', views.get_all_popups, name='get_all_popups'),
    path('popups/<int:pk>/', views.get_popup, name='get_popup'),

    # Offers
    path('offers/', views.get_all_offers, name='get_all_offers'),
    path('offers/<int:pk>/', views.get_offer, name='get_offer'),

    # Core Modules
    path('modules/', views.get_all_modules, name='get_all_modules'),
    path('modules/<int:pk>/', views.get_module, name='get_module'),

    # Location
    path('location/', views.get_location, name='get_location'),

    # Site Preferences
    path('site-preferences/', views.get_site_preferences, name='get_site_preferences'),

    # Media
    path('media/', views.get_all_media, name='get_all_media'),
    path('media/<int:pk>/', views.get_media, name='get_media'),
    path('media-folders/', views.get_all_media_folders, name='get_all_media_folders'),

    # Universal Slug API (Fallback route, should be at the bottom)
    path('<slug:slug>/', views.get_by_slug, name='get_by_slug'),
]