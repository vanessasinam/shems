from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse

from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

from .forms import NewUserForm
from shemsWebapp.models import Customer

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            customer = Customer.objects.create(user=user)
            customer.user = user
            customer.first_name = "First Name"
            customer.last_name = "Last Name"
            customer.billing_address = "Address"
            customer.save()
            return redirect("shemsAccount:login")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return render(request, "registration/register.html", {'form': form})
    else:
        form = NewUserForm()
    context = {}
    context["form"] = form
    return render(
        request=request, template_name="registration/register.html", context=context
    )

def login_view(request):
    form = AuthenticationForm()
    context = {}
    context["form"] = form
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse("shemsWebapp:profile"))
            else:
                return render(request, "registration/login.html", context)
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return render(request, "registration/login.html", context)
    else:
        return render(request, "registration/login.html", context)

def logout_view(request):
    logout(request)
    return redirect("shemsAccount:home")

def home(request):
    if request.user.is_authenticated:
        return redirect("shemsWebapp:profile")
    else:
        return redirect("shemsAccount:login")