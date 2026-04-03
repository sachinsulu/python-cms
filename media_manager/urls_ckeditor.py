# media_manager/urls_ckeditor.py
"""
Minimal URL conf that maps CKEditor's upload POST to our custom view.
Included at ckeditor/upload/ in cms/urls.py — takes priority over the
default ckeditor_uploader.urls browse/upload endpoints.
"""
from django.urls import path
from .ckeditor_views import ckeditor_upload, ckeditor_browse

urlpatterns = [
    path("", ckeditor_upload, name="ckeditor_custom_upload"),
    path("browse/", ckeditor_browse, name="ckeditor_custom_browse"),
]
