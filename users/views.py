from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib import messages


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_active']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


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
        return redirect('user_list')
    return render(request, 'users/form.html', {'form': form})


@login_required
def user_edit(request, id):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage users.")
        return redirect('dashboard')
    user = get_object_or_404(User, id=id)
    form = UserCreateForm(request.POST or None, instance=user)

    # IMPORTANT: password optional on edit
    form.fields['password'].required = False

    if form.is_valid():
        if form.cleaned_data.get('password'):
            user.set_password(form.cleaned_data['password'])
        form.save()
        return redirect('user_list')

    return render(request, 'users/form.html', {
        'form': form,
        'edit': True
    })

@login_required
def user_delete(request, id):
    user = get_object_or_404(User, id=id)

    # Prevent deleting superuser or self
    if user.is_superuser or user == request.user:
        return redirect('user_list')

    if request.method == 'POST':
        user.delete()
    return redirect('user_list')
