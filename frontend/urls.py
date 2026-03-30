from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('rooms', views.rooms, name='rooms'),
    path('<slug:slug>/', views.room_details, name='room_details'),
    path('hall', views.hall, name='hall'),
    path('restaurant', views.restaurant, name='restaurant'),
    path('amenities', views.amenities, name='amenities'),
    path('gallery', views.gallery, name='gallery'),
    path('contact', views.contact, name='contact'),
    path('nearby', views.nearby, name='nearby'),
    path('spa', views.spa, name='spa'),
]
