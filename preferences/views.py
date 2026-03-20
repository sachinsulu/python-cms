import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from users.decorators import requires_perm
from .models import SitePreferences
from .forms import SitePreferencesForm
from core.models import Module, PageMeta
from core.forms import PageMetaForm

logger = logging.getLogger(__name__)


@login_required
@requires_perm('preferences.change_sitepreferences')
@require_http_methods(['GET', 'POST'])
def preference_edit(request):
    instance = SitePreferences.objects.get_solo()

    if request.method == 'POST':
        form = SitePreferencesForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site preferences saved successfully.')
            return redirect('preference_edit')
        else:
            logger.warning('Preferences form errors: %s', form.errors)
    else:
        form = SitePreferencesForm(instance=instance)

    module = Module.objects.filter(url_name='preference_edit').first()
    page_meta = None
    if module:
        try:
            page_meta = module.page_meta
        except PageMeta.DoesNotExist:
            page_meta = None

    page_meta_form = PageMetaForm(instance=page_meta)

    return render(request, 'preferences/form.html', {
        'form':     form,
        'instance': instance,
        'page_meta': page_meta,
        'page_meta_form': page_meta_form,
        'module_url_name': 'preference_edit',
    })