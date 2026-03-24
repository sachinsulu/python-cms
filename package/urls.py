from django.urls import path
from . import views

urlpatterns = [
    # Package
    path('', views.package_list, name='package_list'),
    path('create/', views.package_create, name='package_create'),
    path('edit/<slug:slug>/', views.package_edit, name='package_edit'),

    # SubPackage
    path('<slug:package_slug>/sub/', views.subpackage_list, name='subpackage_list'),
    path('<slug:package_slug>/sub/create/', views.subpackage_create, name='subpackage_create'),
    path('<slug:package_slug>/sub/edit/<slug:slug>/', views.subpackage_edit, name='subpackage_edit'),
]