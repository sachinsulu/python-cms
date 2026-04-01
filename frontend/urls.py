from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/<slug:slug>', views.about, name='about'),
    path('rooms', views.rooms, name='rooms'),
    path('amenities', views.amenities, name='amenities'),
    path('gallery', views.gallery, name='gallery'),
    path('contact', views.contact, name='contact'),
    path('<slug:slug>/', views.dynamic_detail, name='dynamic_detail'),
]
