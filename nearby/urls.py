from django.urls import path
from . import views

urlpatterns = [
    path('', views.nearby_list, name='nearby_list'),
    path('create/', views.create_nearby, name='create_nearby'),
    path('edit/<int:pk>/', views.edit_nearby, name='edit_nearby')


]