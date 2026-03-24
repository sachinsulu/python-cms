from django.shortcuts import render, redirect, get_object_or_404
from .models import Nearby
from .forms import NearbyForm
from django.contrib.auth.decorators import login_required
from users.decorators import requires_perm
from django.contrib import messages
from django.urls import reverse
from core.utils import get_page_meta_context
@login_required
@requires_perm('nearby.view_nearby')
def nearby_list(request):
    nearby = Nearby.objects.all().order_by('position')

    return render(request, 'nearby/list.html', {
        'list': nearby,
        **get_page_meta_context('nearby_list'),
    })


@login_required
@requires_perm('nearby.add_nearby')
def create_nearby(request):
    if request.method == 'POST':
        form = NearbyForm(request.POST, request.FILES)
        if form.is_valid():
            nearby = form.save(commit=False)
            nearby.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_quit':
                return redirect('nearby_list')
            else:
                messages.success(request, "Nearby saved!")
                return redirect(reverse('edit_nearby', args=[nearby.pk]))
    else:
        form = NearbyForm()

    return render(request, 'nearby/form.html', {
        'form': form,
    })


@login_required
@requires_perm('nearby.change_nearby')
def edit_nearby(request, pk):
    nearby = get_object_or_404(Nearby, pk=pk)

    if request.method == 'POST':
        form = NearbyForm(request.POST, request.FILES, instance=nearby)
        if form.is_valid():
            nearby = form.save(commit=False)
            nearby.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_quit':
                return redirect('nearby_list')
            else:
                messages.success(request, "Nearby saved!")
                return redirect(reverse('edit_nearby', args=[nearby.pk]))
    else:
        form = NearbyForm(instance=nearby)

    return render(request, 'nearby/form.html', {
        'form': form,
        'is_edit': True,
        'nearby': nearby,
    })