import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from users.decorators import requires_perm
from .forms import TestimonialForm
from .models import Testimonial
from core.models import Module, PageMeta
from core.forms import PageMetaForm

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@login_required
@requires_perm('testimonials.view_testimonial')
def testimonial_list(request):
    testimonials = Testimonial.objects.all().order_by('position')

    module = Module.objects.filter(url_name='testimonial_list').first()
    page_meta = None
    if module:
        try:
            page_meta = module.page_meta
        except PageMeta.DoesNotExist:
            page_meta = None

    page_meta_form = PageMetaForm(instance=page_meta)

    return render(request, 'testimonials/list.html', {
        'list': testimonials,
        'page_meta': page_meta,
        'page_meta_form': page_meta_form,
        'module_url_name': 'testimonial_list',
    })


@login_required
@requires_perm('testimonials.add_testimonial')
def testimonial_create(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            testimonial = form.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                messages.success(request, "Testimonial saved! You can create a new one now.")
                return redirect('testimonial_create')
            elif action == 'save_and_quit':
                return redirect('testimonial_list')
            else:
                messages.success(request, "Testimonial saved!")
                return redirect(reverse('testimonial_edit', args=[testimonial.pk]))
        else:
            logger.warning("Testimonial create form errors: %s", form.errors)
    else:
        form = TestimonialForm()

    return render(request, 'testimonials/form.html', {'form': form})


@login_required
@requires_perm('testimonials.change_testimonial')
def testimonial_edit(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)

    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            testimonial = form.save(commit=False)

            # Handle image removal
            if request.POST.get('remove_image') == '1':
                testimonial.image = None

            testimonial.save()
            action = request.POST.get('action', 'save')
            if action == 'save_and_new':
                return redirect('testimonial_create')
            elif action == 'save_and_quit':
                return redirect('testimonial_list')
            else:
                messages.success(request, "Testimonial updated!")
                return redirect(reverse('testimonial_edit', args=[testimonial.pk]))
        else:
            logger.warning("Testimonial edit form errors: %s", form.errors)
    else:
        form = TestimonialForm(instance=testimonial)

    return render(request, 'testimonials/form.html', {
        'form': form,
        'is_edit': True,
        'testimonial': testimonial,
    })