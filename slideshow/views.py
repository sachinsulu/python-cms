import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from users.decorators import requires_perm
from .forms import SlideshowForm
from .models import Slideshow

logger = logging.getLogger(__name__)

SESSION_KEY = 'slideshow_type_filter'


@ensure_csrf_cookie
@login_required
@requires_perm('slideshow.view_slideshow')
def slideshow_list(request):
    type_param = request.GET.get('type')

    if type_param is not None:
        request.session[SESSION_KEY] = type_param
        return redirect('slideshow_list')

    current_filter = request.session.get(SESSION_KEY, Slideshow.TYPE_IMAGE)
    items = Slideshow.objects.filter(type=current_filter).order_by('position')

    return render(request, 'slideshow/list.html', {
        'list':           items,
        'current_filter': current_filter,
        'type_image':     Slideshow.TYPE_IMAGE,
        'type_video':     Slideshow.TYPE_VIDEO,
    })


@login_required
@requires_perm('slideshow.add_slideshow')
def slideshow_create(request):
    current_type = request.session.get(SESSION_KEY, Slideshow.TYPE_IMAGE)

    if request.method == 'POST':
        form = SlideshowForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.type = current_type

            if request.POST.get('remove_image') == '1':
                item.image = None

            item.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Slide saved! You can create a new one.")
                return redirect('slideshow_create')
            elif action == 'save_and_quit':
                return redirect('slideshow_list')
            else:
                messages.success(request, "Slide saved!")
                return redirect(reverse('slideshow_edit', args=[item.pk]))
        else:
            logger.warning("Slideshow create errors: %s", form.errors)
    else:
        form = SlideshowForm()

    return render(request, 'slideshow/form.html', {
        'form':         form,
        'current_type': current_type,
    })


@login_required
@requires_perm('slideshow.change_slideshow')
def slideshow_edit(request, pk):
    item         = get_object_or_404(Slideshow, pk=pk)
    current_type = request.session.get(SESSION_KEY, Slideshow.TYPE_IMAGE)

    if request.method == 'POST':
        form = SlideshowForm(request.POST, instance=item)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.type = current_type

            if request.POST.get('remove_image') == '1':
                obj.image = None

            obj.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('slideshow_create')
            elif action == 'save_and_quit':
                return redirect('slideshow_list')
            else:
                messages.success(request, "Slide updated!")
                return redirect(reverse('slideshow_edit', args=[obj.pk]))
        else:
            logger.warning("Slideshow edit errors: %s", form.errors)
    else:
        initial = {}
        if item.image_id:
            initial['image_media'] = item.image_id
        form = SlideshowForm(instance=item, initial=initial)

    return render(request, 'slideshow/form.html', {
        'form':         form,
        'is_edit':      True,
        'item':         item,
        'current_type': current_type,
    })