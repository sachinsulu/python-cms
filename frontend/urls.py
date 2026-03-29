from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index.html', views.home, name='index'),
    path('about.html', views.about, name='about'),
    path('rooms.html', views.rooms, name='rooms'),
    path('room-details.html', views.room_details, name='room_details'),
    path('hall.html', views.hall, name='hall'),
    path('restaurant.html', views.restaurant, name='restaurant'),
    path('amenities.html', views.amenities, name='amenities'),
    path('gallery.html', views.gallery, name='gallery'),
    path('contact.html', views.contact, name='contact'),
    path('nearby.html', views.nearby, name='nearby'),
    path('spa.html', views.spa, name='spa'),
]
