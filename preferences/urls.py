from django.urls import path
from . import views

urlpatterns = [
    path('', views.preference_edit, name='preference_edit'),
]