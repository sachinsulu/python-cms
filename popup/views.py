# popup/views.py
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from users.decorators import requires_perm
from .forms import PopupForm
from .models import Popup

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@login_required
@requires_perm('popup.view_popup')
def popup_list(request):
    items = Popup.objects.all()
    return render(request, 'popup/list.html', {'list': items})


@login_required
@requires_perm('popup.add_popup')
def popup_create(request):
    if request.method == 'POST':
        form = PopupForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)

            if request.POST.get('remove_file') == '1':
                item.file = None

            item.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Saved! You can create a new one.")
                return redirect('popup_create')
            elif action == 'save_and_quit':
                return redirect('popup_list')
            else:
                messages.success(request, "Popup saved!")
                return redirect(reverse('popup_edit', args=[item.pk]))
        else:
            logger.warning("Popup create errors: %s", form.errors)
    else:
        form = PopupForm()

    return render(request, 'popup/form.html', {'form': form})


@login_required
@requires_perm('popup.change_popup')
def popup_edit(request, pk):
    item = get_object_or_404(Popup, pk=pk)

    if request.method == 'POST':
        form = PopupForm(request.POST, instance=item)
        if form.is_valid():
            obj = form.save(commit=False)

            if request.POST.get('remove_file') == '1':
                obj.file = None

            obj.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('popup_create')
            elif action == 'save_and_quit':
                return redirect('popup_list')
            else:
                messages.success(request, "Popup updated!")
                return redirect(reverse('popup_edit', args=[obj.pk]))
        else:
            logger.warning("Popup edit errors: %s", form.errors)
    else:
        # Pre-populate picker with current Media pk
        initial = {}
        if item.file_id:
            initial['file_media'] = item.file_id
        form = PopupForm(instance=item, initial=initial)

    return render(request, 'popup/form.html', {
        'form':    form,
        'is_edit': True,
        'item':    item,
    })