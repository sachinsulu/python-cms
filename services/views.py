import json
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from articles.models import Article
from blog.models import Blog
from package.models import Package, SubPackage

from users.decorators import requires_perm
from .forms import ServiceForm
from .models import Service
from core.models import Module, PageMeta
from core.forms import PageMetaForm
logger = logging.getLogger(__name__)

SESSION_KEY = 'service_type_filter'


def _slug_json(queryset, title_field='title'):
    return json.dumps([
        {'title': str(getattr(obj, title_field)), 'slug': obj.slug}
        for obj in queryset
    ])


def _picker_context():
    return {
        'articles_json':    _slug_json(Article.objects.filter(active=True).order_by('title')),
        'blogs_json':       _slug_json(Blog.objects.filter(active=True).order_by('title')),
        'packages_json':    _slug_json(Package.objects.filter(is_active=True).order_by('title')),
        'subpackages_json': _slug_json(SubPackage.objects.filter(is_active=True).order_by('title')),
    }


@ensure_csrf_cookie
@login_required
@requires_perm('services.view_service')
def service_list(request):
    type_param = request.GET.get('type')

    if type_param is not None:
        request.session[SESSION_KEY] = type_param
        return redirect('service_list')

    current_filter = request.session.get(SESSION_KEY, Service.TYPE_MAIN_SERVICE)
    items = Service.objects.filter(type=current_filter).order_by('position')

    module = Module.objects.filter(url_name='service_list').first()

    # Get existing PageMeta if it exists
    page_meta = None
    if module:
        try:
            page_meta = module.page_meta
        except PageMeta.DoesNotExist:
            page_meta = None

    # Pre-fill form with existing data
    page_meta_form = PageMetaForm(instance=page_meta)

    return render(request, 'services/list.html', {
        'list': items,
        'current_filter': current_filter,
        'type_main_service': Service.TYPE_MAIN_SERVICE,
        'type_service': Service.TYPE_SERVICE,
        'page_meta':        page_meta,
        'page_meta_form':   page_meta_form,
        'module_url_name':  'service_list',
    })


@login_required
@requires_perm('services.add_service')
def service_create(request):
    current_type = request.session.get(SESSION_KEY, Service.TYPE_MAIN_SERVICE)

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.type = current_type
            item.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Saved! You can create a new one.")
                return redirect('service_create')
            elif action == 'save_and_quit':
                return redirect('service_list')
            else:
                messages.success(request, "Saved!")
                return redirect(reverse('service_edit', args=[item.pk]))
        else:
            logger.warning("Service create errors: %s", form.errors)
    else:
        form = ServiceForm()

    return render(request, 'services/form.html', {
        'form': form,
        'current_type': current_type,
        **_picker_context(),
    })


@login_required
@requires_perm('services.change_service')
def service_edit(request, pk):
    item = get_object_or_404(Service, pk=pk)
    current_type = request.session.get(SESSION_KEY, Service.TYPE_MAIN_SERVICE)

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.type = current_type

            if request.POST.get('remove_image') == '1':
                obj.image = None

            obj.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('service_create')
            elif action == 'save_and_quit':
                return redirect('service_list')
            else:
                messages.success(request, "Updated!")
                return redirect(reverse('service_edit', args=[obj.pk]))
        else:
            logger.warning("Service edit errors: %s", form.errors)
    else:
        form = ServiceForm(instance=item)

    return render(request, 'services/form.html', {
        'form': form,
        'is_edit': True,
        'item': item,
        'current_type': current_type,
        **_picker_context(),
    })
