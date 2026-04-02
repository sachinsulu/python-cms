from django.http import Http404
from django.shortcuts import render
from core.models import GlobalSlug

def route_slug(request, slug):
    obj = GlobalSlug.resolve(slug)
    if not obj:
        raise Http404("Page not found")

    model_name = obj._meta.model_name

    # Article
    if model_name == 'article':
        if not getattr(obj, 'active', True):
            raise Http404("Page not found")
        return render(request, 'hotelrudra/about.html', {'article': obj})

    # Blog
    if model_name == 'blog':
        if not getattr(obj, 'active', True):
            raise Http404("Page not found")
        return render(request, 'hotelrudra/blog-detail.html', {'blog': obj})

    # Package
    if model_name == 'package':
        if not getattr(obj, 'is_active', True):
            raise Http404("Page not found")
        sub_packages = obj.sub_packages.filter(is_active=True)\
            .select_related('image')\
            .prefetch_related('amenity_links__feature__image')\
            .order_by('position')
        return render(request, 'hotelrudra/package-detail.html', {
            'package': obj,
            'sub_packages': sub_packages,
        })

    # SubPackage
    if model_name == 'subpackage':
        if not getattr(obj, 'is_active', True):
            raise Http404("Page not found")
        if obj.package.package_type == 'room':
            return render(request, 'hotelrudra/room-details.html', {'room': obj})
        return render(request, 'hotelrudra/sub-detail.html', {'room': obj})

    # Unknown content type
    raise Http404("Content not found")