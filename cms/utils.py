from django.apps import apps
from django.db.models import Model

def is_slug_taken(slug, exclude_obj=None):
    """
    Checks if a slug is taken across Article, Blog, Package, and SubPackage models.
    
    Args:
        slug (str): The slug to check.
        exclude_obj (Model, optional): An object instance to exclude from the check (useful for edits).
        
    Returns:
        bool: True if the slug is taken, False otherwise.
    """
    models_to_check = [
        ('articles', 'Article'),
        ('blog', 'Blog'),
        ('package', 'Package'),
        ('package', 'SubPackage'),
    ]
    
    for app_label, model_name in models_to_check:
        try:
            model = apps.get_model(app_label, model_name)
            
            # Robustness: Skip models that don't have a 'slug' field
            try:
                model._meta.get_field('slug')
            except Exception:
                continue

            qs = model.objects.filter(slug=slug)
            
            if exclude_obj and isinstance(exclude_obj, model):
                qs = qs.exclude(pk=exclude_obj.pk)
                
            if qs.exists():
                return True
        except (LookupError, AttributeError):
            continue
            
    return False
