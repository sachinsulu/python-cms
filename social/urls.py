from django.urls import path
from . import views

urlpatterns = [
    path('', views.social_list, name='social_list'),
    path('create/', views.social_create, name='social_create'),
    path('edit/<int:pk>/', views.social_edit, name='social_edit'),
]