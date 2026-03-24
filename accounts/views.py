from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_POST


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("dashboard")

        messages.error(request, "Invalid username or password")

    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")