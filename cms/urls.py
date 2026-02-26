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
from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view, logout_view
from .views import dashboard, toggle_status,delete_object,bulk_action,update_order,ajax_check_slug
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('users/', include('users.urls')),
    path('module/', include('core.urls')),
    path('articles/', include('articles.urls')),
    path('blog/', include('blog.urls')),
    path('api/', include('api.urls')),
    path('packages/', include('package.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('toggle-status/<str:model_name>/<int:pk>/', toggle_status, name='toggle_status'),
    path("delete_object/<str:model_name>/<int:pk>/", delete_object, name="delete_object"),
    path('bulk/<str:model_name>/', bulk_action, name='bulk_action'),
    path('sort/<str:model_name>/', update_order, name='sort'),
    path('ajax/check-slug/<str:model_name>/', ajax_check_slug, name='ajax_check_slug'),
    path("__reload__/", include("django_browser_reload.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)