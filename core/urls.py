from django.urls import path
from . import views

urlpatterns = [
    path('', views.module_list, name='module_list'),
    path('create/', views.module_create, name='module_create'),
    path('edit/<int:pk>/', views.module_edit, name='module_edit'),
    path('delete/<int:pk>/', views.module_delete, name='module_delete'),
]