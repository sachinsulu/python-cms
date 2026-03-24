from django.urls import path
from . import views

urlpatterns = [
    path('', views.popup_list, name='popup_list'),
    path('create/', views.popup_create, name='popup_create'),
    path('edit/<int:pk>/', views.popup_edit, name='popup_edit'),
]
