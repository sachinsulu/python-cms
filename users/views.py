from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib import messages

# ------------------------------
# USER FORMS
# ------------------------------
class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_active', 'groups']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['groups'])
        return user


# ------------------------------
# GROUP FORMS
# ------------------------------
class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.filter(
            content_type__app_label__in=['articles', 'auth', 'package', 'blog']
        ).select_related('content_type'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

# ------------------------------
# USER VIEWS
# ------------------------------
@login_required
def user_list(request):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage users.")
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})


@login_required
def user_create(request):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage users.")
        return redirect('dashboard')

    form = UserCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "User created successfully!")
        return redirect('user_list')

    return render(request, 'users/form.html', {'form': form})


@login_required
def user_edit(request, id):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage users.")
        return redirect('dashboard')

    user = get_object_or_404(User, id=id)
    form = UserCreateForm(request.POST or None, instance=user)
    form.fields['password'].required = False

    if form.is_valid():
        form.save()
        messages.success(request, "User updated successfully!")
        return redirect('user_list')

    return render(request, 'users/form.html', {'form': form, 'edit': True})


@login_required
def user_delete(request, id):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage users.")
        return redirect('dashboard')

    user = get_object_or_404(User, id=id)

    if user.is_superuser:
        messages.error(request, "Cannot delete a superuser account.")
        return redirect('user_list')

    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')

    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect('user_list')

    return render(request, 'users/delete.html', {'user': user})

# ------------------------------
# GROUP VIEWS
# ------------------------------
@login_required
def group_list(request):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage groups.")
        return redirect('dashboard')
    groups = Group.objects.all()
    return render(request, 'users/group_list.html', {'groups': groups})


@login_required
def group_create(request):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage groups.")
        return redirect('dashboard')

    form = GroupForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Group created successfully!")
        return redirect('group_list')

    return render(request, 'users/group_form.html', {'form': form})


@login_required
def group_edit(request, id):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage groups.")
        return redirect('dashboard')

    group = get_object_or_404(Group, id=id)
    form = GroupForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save()
        messages.success(request, "Group updated successfully!")
        return redirect('group_list')

    return render(request, 'users/group_form.html', {'form': form})