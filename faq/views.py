from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from users.decorators import requires_perm
from .models import FAQ
from .forms import FAQForm

@login_required
@requires_perm('faq.view_faq')
def faq_list(request):
    list = FAQ.objects.all().order_by('position')
    return render(request, 'faq/list.html', {'list': list})

@login_required
@requires_perm('faq.add_faq')
def faq_create(request):
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Get the highest position
                last_pos = FAQ.objects.aggregate(Max('position'))['position__max']
                new_pos = (last_pos or 0) + 1
                
                faq = form.save(commit=False)
                faq.position = new_pos
                faq.save()
                
                messages.success(request, 'FAQ created successfully!')
                return redirect('faq_list')
    else:
        form = FAQForm()
    return render(request, 'faq/form.html', {'form': form, 'title': 'Create FAQ'})

@login_required
@requires_perm('faq.change_faq')
def faq_edit(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ updated successfully!')
            return redirect('faq_list')
    else:
        form = FAQForm(instance=faq)
    return render(request, 'faq/form.html', {'form': form, 'title': 'Edit FAQ'})

