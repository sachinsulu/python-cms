from django.urls import path
from . import views

urlpatterns = [
    path('', views.slideshow_list, name='slideshow_list'),
    path('create/', views.slideshow_create, name='slideshow_create'),
    path('edit/<int:pk>/', views.slideshow_edit, name='slideshow_edit'),
]