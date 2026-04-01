from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from core.models import GlobalSlug
from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage

def _sync_slug(instance):
    content_type = ContentType.objects.get_for_model(instance)
    GlobalSlug.objects.update_or_create(
        content_type=content_type,
        object_id=instance.pk,
        defaults={'slug': instance.slug},
    )

for model in (Article, Blog, Package, SubPackage):
    @receiver(post_save, sender=model)
    def _handler(sender, instance, **kwargs):
        _sync_slug(instance)
