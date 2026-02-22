from django.urls import path
from . import views

urlpatterns = [
    # ------------------ Users ------------------
    path('', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/edit/<int:id>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:id>/', views.user_delete, name='user_delete'),

    # ------------------ Groups ------------------
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/edit/<int:id>/', views.group_edit, name='group_edit'),
]