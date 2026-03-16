from django.urls import path
from . import views

urlpatterns = [
    # Feature Group routes
    path('', views.feature_group_list, name='feature_group_list'),
    path('group/create/', views.feature_group_create, name='feature_group_create'),
    path('group/edit/<int:pk>/', views.feature_group_edit, name='feature_group_edit'),

    # Feature routes scoped under groups
    path('group/<int:group_id>/features/', views.feature_list, name='feature_list'),
    path('group/<int:group_id>/features/create/', views.feature_create, name='feature_create'),
    path('group/<int:group_id>/features/edit/<int:pk>/', views.feature_edit, name='feature_edit'),
]