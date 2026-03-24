from django import forms
from django.contrib.auth.models import Group
from .models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Role"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            groups = self.instance.groups.all()
            self.fields['role'].initial = groups.first()

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            user.groups.clear()
            if self.cleaned_data['role']:
                user.groups.add(self.cleaned_data['role'])
        return user
