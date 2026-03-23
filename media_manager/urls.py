from django.urls import path
from . import views

urlpatterns = [
    path("", views.media_library, name="media_library"),
    path("folder/<int:folder_id>/", views.media_library, name="media_folder"),
    path("upload/", views.upload_media, name="upload_media"),
    path("upload/<int:folder_id>/", views.upload_media, name="upload_media_in_folder"),
    path("folder/create/", views.create_folder, name="create_folder"),
    path("delete/<int:media_id>/", views.delete_media, name="delete_media"),
]