from django.urls import path
from . import views

urlpatterns = [
    path('', views.offer_list, name='offer_list'),
    path('create/', views.offer_create, name='offer_create'),
    path('edit/<int:pk>/', views.offer_edit, name='offer_edit'),
]