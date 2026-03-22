import logging
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from users.decorators import requires_perm
from .models import Location
from .forms import LocationForm

logger = logging.getLogger(__name__)


@login_required
@requires_perm('location.change_location')
@require_http_methods(['GET', 'POST'])
def location_edit(request):
    instance = Location.objects.get_solo()

    if request.method == 'POST':
        form = LocationForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location settings saved successfully.')
            return redirect('location_edit')
        else:
            logger.warning('Location form errors: %s', form.errors)
    else:
        form = LocationForm(instance=instance)

    return render(request, 'location/form.html', {
        'form':     form,
        'instance': instance,
    })
