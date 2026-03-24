from django.urls import path
from . import views

urlpatterns = [
    path('', views.faq_list, name='faq_list'),
    path('create/', views.faq_create, name='faq_create'),
    path('edit/<int:pk>/', views.faq_edit, name='faq_edit')


]