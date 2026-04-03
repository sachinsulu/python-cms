"""
URL configuration for cms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve as static_serve
from django.http import HttpResponseNotFound
from accounts.views import login_view, logout_view
from .views import dashboard, toggle_status, delete_object, bulk_action, update_order, ajax_check_slug
from django.conf import settings
from django.conf.urls.static import static



# ── CMS panel routes (all under /apanel/) ──────────────────────────────────
cms_patterns = [
    path('', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('users/', include('users.urls')),
    path('module/', include('core.urls')),
    path('articles/', include('articles.urls')),
    path('blog/', include('blog.urls')),
    path('packages/', include('package.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('social/', include('social.urls')),
    path('nearby/', include('nearby.urls')),
    path('faq/', include('faq.urls')),
    path('menu/', include('menu.urls')),
    path('features/', include('features.urls')),
    path('services/', include('services.urls')),
    path('offers/', include('offers.urls')),
    path('media/', include('media_manager.urls')),
    path('popup/', include('popup.urls')),
    path('location/', include('location.urls')),
    path('preferences/', include('preferences.urls')),
    path('slideshow/', include('slideshow.urls')),
    path('gallery/', include('gallery.urls')),
    path('toggle-status/<str:model_name>/<int:pk>/', toggle_status, name='toggle_status'),
    path('delete_object/<str:model_name>/<int:pk>/', delete_object, name='delete_object'),
    path('bulk/<str:model_name>/', bulk_action, name='bulk_action'),
    path('sort/<str:model_name>/', update_order, name='sort'),
    path('ajax/check-slug/<str:model_name>/', ajax_check_slug, name='ajax_check_slug'),
]

# ── Root URL patterns ──────────────────────────────────────────────────────
urlpatterns = [
    # CMS admin panel
    path('apanel/', include(cms_patterns)),

    # REST API (unchanged — used by frontend)
    path('api/', include('api.urls')),

    # Django built-ins
    path('admin/', admin.site.urls),
    # ── CKEditor upload: override with our custom view ─────────────────────────
    # This MUST come before include('ckeditor_uploader.urls') so Django matches
    # the upload path first and routes it through MediaService.
    path('ckeditor/upload/', include('media_manager.urls_ckeditor')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]


if settings.DEBUG:
    urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ── HotelRudra frontend (catch-all — must be LAST) ─────────────────────────
# Serves the hotelrudra/ directory at the root URL.
# All /api/, /apanel/, /admin/ routes above take priority.


urlpatterns += [
    path('', include('frontend.urls')),
]