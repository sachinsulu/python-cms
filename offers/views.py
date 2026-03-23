# offers/views.py
import json
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from users.decorators import requires_perm
from .forms import OfferForm
from .models import Offer
from core.models import Module, PageMeta
from core.forms import PageMetaForm

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@login_required
@requires_perm('offers.view_offer')
def offer_list(request):
    items     = Offer.objects.all().order_by('position')
    module    = Module.objects.filter(url_name='offer_list').first()
    page_meta = None
    if module:
        try:
            page_meta = module.page_meta
        except PageMeta.DoesNotExist:
            pass

    page_meta_form = PageMetaForm(instance=page_meta)

    return render(request, 'offers/list.html', {
        'list':            items,
        'page_meta':       page_meta,
        'page_meta_form':  page_meta_form,
        'module_url_name': 'offer_list',
    })


@login_required
@requires_perm('offers.add_offer')
def offer_create(request):
    if request.method == 'POST':
        form      = OfferForm(request.POST)
        tiers_raw = request.POST.get('tiers_json', '[]')

        if form.is_valid():
            offer = form.save(commit=False)

            if request.POST.get('remove_image') == '1':
                offer.image = None

            try:
                offer.tiers = json.loads(tiers_raw)
            except (json.JSONDecodeError, ValueError):
                offer.tiers = []

            offer.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Offer saved! You can create a new one.")
                return redirect('offer_create')
            elif action == 'save_and_quit':
                return redirect('offer_list')
            else:
                messages.success(request, "Offer saved!")
                return redirect(reverse('offer_edit', args=[offer.pk]))
        else:
            logger.warning("Offer create errors: %s", form.errors)
    else:
        form = OfferForm()

    return render(request, 'offers/form.html', {'form': form})


@login_required
@requires_perm('offers.change_offer')
def offer_edit(request, pk):
    offer = get_object_or_404(Offer, pk=pk)

    if request.method == 'POST':
        form      = OfferForm(request.POST, instance=offer)
        tiers_raw = request.POST.get('tiers_json', '[]')

        if form.is_valid():
            obj = form.save(commit=False)

            if request.POST.get('remove_image') == '1':
                obj.image = None

            try:
                obj.tiers = json.loads(tiers_raw)
            except (json.JSONDecodeError, ValueError):
                obj.tiers = []

            obj.save()

            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('offer_create')
            elif action == 'save_and_quit':
                return redirect('offer_list')
            else:
                messages.success(request, "Offer updated!")
                return redirect(reverse('offer_edit', args=[obj.pk]))
        else:
            logger.warning("Offer edit errors: %s", form.errors)
    else:
        initial = {}
        if offer.image_id:
            initial['image_media'] = offer.image_id
        form = OfferForm(instance=offer, initial=initial)

    return render(request, 'offers/form.html', {
        'form':       form,
        'is_edit':    True,
        'item':       offer,
        'tiers_json': json.dumps(offer.tiers),
    })