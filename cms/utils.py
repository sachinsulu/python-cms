from django.apps import apps
from django.db.models import Model

def is_slug_taken(slug, exclude_obj=None):
    """
    Checks if a slug is taken across tracked models via the GlobalSlug database.
    
    Args:
        slug (str): The slug to check.
        exclude_obj (Model, optional): An object instance to exclude from the check (useful for edits).
        
    Returns:
        bool: True if the slug is taken, False otherwise.
    """
    from core.models import GlobalSlug
    from django.contrib.contenttypes.models import ContentType

    qs = GlobalSlug.objects.filter(slug=slug)

    if exclude_obj and exclude_obj.pk:
        content_type = ContentType.objects.get_for_model(exclude_obj)
        qs = qs.exclude(content_type=content_type, object_id=exclude_obj.pk)

    return qs.exists()
