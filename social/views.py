import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from users.decorators import requires_perm
from .forms import SocialForm
from .models import Social

logger = logging.getLogger(__name__)

SESSION_KEY = 'social_type_filter'


@ensure_csrf_cookie
@login_required
@requires_perm('social.view_social')
def social_list(request):
    type_param = request.GET.get('type')

    if type_param is not None:
        request.session[SESSION_KEY] = type_param
        return redirect('social_list')

    current_filter = request.session.get(SESSION_KEY, Social.TYPE_SOCIAL)
    items = Social.objects.filter(type=current_filter).order_by('position')

    return render(request, 'social/list.html', {
        'list': items,
        'current_filter': current_filter,
        'type_social': Social.TYPE_SOCIAL,
        'type_ota': Social.TYPE_OTA,
    })


@login_required
@requires_perm('social.add_social')
def social_create(request):
    current_type = request.session.get(SESSION_KEY, Social.TYPE_SOCIAL)

    if request.method == 'POST':
        form = SocialForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.type = current_type
            item.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Saved! You can create a new one.")
                return redirect('social_create')
            elif action == 'save_and_quit':
                return redirect('social_list')
            else:
                messages.success(request, "Saved!")
                return redirect(reverse('social_edit', args=[item.pk]))
        else:
            logger.warning("Social create errors: %s", form.errors)
    else:
        form = SocialForm()

    return render(request, 'social/form.html', {
        'form': form,
        'current_type': current_type,
    })


@login_required
@requires_perm('social.change_social')
def social_edit(request, pk):
    item = get_object_or_404(Social, pk=pk)
    current_type = request.session.get(SESSION_KEY, Social.TYPE_SOCIAL)

    if request.method == 'POST':
        form = SocialForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.type = current_type

            if request.POST.get('remove_image') == '1':
                obj.image = None

            obj.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('social_create')
            elif action == 'save_and_quit':
                return redirect('social_list')
            else:
                messages.success(request, "Updated!")
                return redirect(reverse('social_edit', args=[obj.pk]))
        else:
            logger.warning("Social edit errors: %s", form.errors)
    else:
        form = SocialForm(instance=item)

    return render(request, 'social/form.html', {
        'form': form,
        'is_edit': True,
        'item': item,
        'current_type': current_type,
    })