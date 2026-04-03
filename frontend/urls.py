from django.urls import path
from . import views
from .slug_router import route_slug

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms', views.rooms, name='rooms'),
    path('amenities', views.amenities, name='amenities'),
    path('gallery', views.gallery, name='gallery'),
    path('contact', views.contact, name='contact'),
    path('enquiry', views.enquiry, name='enquiry'),
    path('services', views.Main_Service, name='Main_Service'),
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    path('blog/<slug:slug>/', route_slug, name='blog_detail'),
    path('<slug:slug>/', route_slug, name='dynamic_detail'),
]
