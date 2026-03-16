from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import requires_perm
from .models import FeatureGroup, Feature
from .forms import FeatureGroupForm, FeatureForm

# =========================
# FeatureGroup Views
# =========================

@login_required
@requires_perm('features.view_featuregroup')
def feature_group_list(request):
    groups = FeatureGroup.objects.all().order_by('position')
    return render(request, 'features/group_list.html', {'groups': groups})

@login_required
@requires_perm('features.add_featuregroup')
def feature_group_create(request):
    form = FeatureGroupForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Feature Group created successfully!")
        return redirect('feature_group_list')
    return render(request, 'features/group_form.html', {'form': form, 'is_edit': False})

@login_required
@requires_perm('features.change_featuregroup')
def feature_group_edit(request, pk):
    group = get_object_or_404(FeatureGroup, pk=pk)
    form = FeatureGroupForm(request.POST or None, request.FILES or None, instance=group)
    if form.is_valid():
        form.save()
        messages.success(request, "Feature Group updated successfully!")
        return redirect('feature_group_list')
    return render(request, 'features/group_form.html', {'form': form, 'is_edit': True, 'group': group})

# =========================
# Feature Views
# =========================

@login_required
@requires_perm('features.view_feature')
def feature_list(request, group_id):
    group = get_object_or_404(FeatureGroup, pk=group_id)
    features = Feature.objects.filter(group=group).order_by('position')
    return render(request, 'features/list.html', {'group': group, 'features': features})

@login_required
@requires_perm('features.add_feature')
def feature_create(request, group_id):
    group = get_object_or_404(FeatureGroup, pk=group_id)
    form = FeatureForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        feature = form.save(commit=False)
        feature.group = group
        feature.save()
        messages.success(request, "Feature created successfully!")
        return redirect('feature_list', group_id=group.id)
    return render(request, 'features/form.html', {'form': form, 'is_edit': False, 'group': group})

@login_required
@requires_perm('features.change_feature')
def feature_edit(request, group_id, pk):
    group = get_object_or_404(FeatureGroup, pk=group_id)
    feature = get_object_or_404(Feature, pk=pk, group=group)
    form = FeatureForm(request.POST or None, request.FILES or None, instance=feature)
    if form.is_valid():
        form.save()
        messages.success(request, "Feature updated successfully!")
        return redirect('feature_list', group_id=group.id)
    return render(request, 'features/form.html', {'form': form, 'is_edit': True, 'feature': feature, 'group': group})