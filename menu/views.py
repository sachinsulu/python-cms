import json
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from users.decorators import requires_perm
from .models import MenuItem
from .forms import MenuItemForm

# Import all slug-having models
from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage

logger = logging.getLogger(__name__)


def _slug_json(queryset, title_field='title'):
    """
    Convert a queryset into a JSON-serializable list of {title, slug} dicts.
    Only includes active/published items so the picker only shows live content.
    """
    return json.dumps([
        {'title': str(getattr(obj, title_field)), 'slug': obj.slug}
        for obj in queryset
    ])


def _picker_context():
    """
    Returns the four JSON blobs needed by the slug picker in the form template.
    Called by both menu_create and menu_edit so it stays DRY.
    """
    return {
        'articles_json':    _slug_json(Article.objects.filter(active=True).order_by('title')),
        'blogs_json':       _slug_json(Blog.objects.filter(active=True).order_by('title')),
        'packages_json':    _slug_json(Package.objects.filter(is_active=True).order_by('title')),
        'subpackages_json': _slug_json(SubPackage.objects.filter(is_active=True).order_by('title')),
    }


@ensure_csrf_cookie
@login_required
@requires_perm('menu.view_menuitem')
def menu_list(request):
    from django.db.models import Prefetch
    items = MenuItem.objects.filter(parent=None).prefetch_related(
        Prefetch('children', queryset=MenuItem.objects.order_by('position'))
    ).order_by('position')
    return render(request, 'menu/list.html', {
        'list': items,
    })


@login_required
@requires_perm('menu.add_menuitem')
def menu_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Menu item saved! You can create a new one.")
                return redirect('menu_create')
            elif action == 'save_and_quit':
                return redirect('menu_list')
            else:
                messages.success(request, "Menu item saved!")
                return redirect(reverse('menu_edit', args=[item.pk]))
        else:
            logger.warning("Menu item create errors: %s", form.errors)
    else:
        form = MenuItemForm()

    return render(request, 'menu/form.html', {
        'form': form,
        **_picker_context(),
    })


@login_required
@requires_perm('menu.change_menuitem')
def menu_edit(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)

    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('menu_create')
            elif action == 'save_and_quit':
                return redirect('menu_list')
            else:
                messages.success(request, "Menu item updated!")
                return redirect(reverse('menu_edit', args=[item.pk]))
        else:
            logger.warning("Menu item edit errors: %s", form.errors)
    else:
        form = MenuItemForm(instance=item)

    return render(request, 'menu/form.html', {
        'form': form,
        'is_edit': True,
        'item': item,
        **_picker_context(),
    })