import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from users.decorators import requires_perm
from .models import SitePreferences
from .forms import SitePreferencesForm, IMAGE_FIELDS

logger = logging.getLogger(__name__)


@login_required
@requires_perm('preferences.change_sitepreferences')
@require_http_methods(['GET', 'POST'])
def preference_edit(request):
    instance = SitePreferences.objects.get_solo()

    if request.method == 'POST':
        form = SitePreferencesForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site preferences saved successfully.')
            return redirect('preference_edit')
        else:
            logger.warning('Preferences form errors: %s', form.errors)
    else:
        # Pre-populate hidden picker fields with current Media PKs
        # so the template knows what is already selected
        initial = {}
        for field in IMAGE_FIELDS:
            media_obj = getattr(instance, field)
            if media_obj:
                initial[f'{field}_media'] = media_obj.pk
        form = SitePreferencesForm(instance=instance, initial=initial)

    # Build a flat dict of current media PKs for the template
    # so the partial can render the correct hidden input value
    # without needing a custom getitem filter
    current_media_pks = {}
    for field in IMAGE_FIELDS:
        media_obj = getattr(instance, field)
        current_media_pks[field] = media_obj.pk if media_obj else ''

    return render(request, 'preferences/form.html', {
        'form':             form,
        'instance':         instance,
        'current_media_pks': current_media_pks,
    })