from django.urls import path
from . import views

urlpatterns = [
    path('', views.location_edit, name='location_edit'),
]
