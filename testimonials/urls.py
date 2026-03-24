from django.urls import path
from . import views

urlpatterns = [
    path('', views.testimonial_list, name='testimonial_list'),
    path('create/', views.testimonial_create, name='testimonial_create'),
    path('edit/<int:pk>/', views.testimonial_edit, name='testimonial_edit'),
]