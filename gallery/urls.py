from django.urls import path
from .views import (
    gallery_list,
    gallery_create,
    gallery_edit,
    gallery_images,
    gallery_image_edit,
    gallery_bulk_add_images,
    gallery_add_youtube,
)

urlpatterns = [
    path('', gallery_list, name='gallery_list'),
    path('create/', gallery_create, name='gallery_create'),
    path('edit/<int:pk>/', gallery_edit, name='gallery_edit'),
    path('<int:pk>/images/', gallery_images, name='gallery_images'),
    path('<int:pk>/images/bulk-add/', gallery_bulk_add_images, name='gallery_bulk_add_images'),
    path('<int:pk>/images/add-youtube/', gallery_add_youtube, name='gallery_add_youtube'),
    path('<int:pk>/images/edit/<int:img_pk>/', gallery_image_edit, name='gallery_image_edit'),
]