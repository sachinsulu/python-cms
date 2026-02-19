from django.urls import path
from . import views

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('create/', views.package_create, name='package_create'),
    path('edit/<slug:slug>/', views.package_edit, name='package_edit'),
]