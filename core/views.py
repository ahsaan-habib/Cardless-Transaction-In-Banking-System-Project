import random
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from banking.models import Account

from .forms import ProfileImageUpdateForm, ProfileUpdateForm, RegistrationForm, AuthenticateForm



def index(request):
    context ={}
    return render(request, 'core/index.html', context)


@login_required(login_url="core:login")
def profile_view(request):
    context = {}
    if request.POST:
        form = ProfileImageUpdateForm(request.POST or None, 
        request.FILES or None, instance=request.user)
        if form.is_valid():
            form.save()
            context['success_message'] = "Updated"
            return HttpResponseRedirect(reverse('core:profile'))
        context['success_message'] = "failed"
    else:
        form = ProfileImageUpdateForm(instance=request.user)

    user = request.user
    account = Account.objects.filter(user=user).first()
    context['account_info'] = account
    context['user'] = user
    context['profile_image_form'] = form
    return render(request, 'core/profile.html', context)


@login_required(login_url="login")
def profile_update_view(request):
    context = {}
    if request.POST:
        form = ProfileUpdateForm(request.POST or None,
            request.FILES or None, instance=request.user)
        if form.is_valid():
            form.save()
            context['success_message'] = "Updated"
            return HttpResponseRedirect(reverse('core:profile'))
        
    else:
        form = ProfileUpdateForm(instance=request.user)
        
    context['account_form'] = form

    return render(request, "core/updateProfile.html", context)


def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            if email:
                user.username = email + str(random.randrange(1, 1000))
            else:
                user.username = phone + str(random.randrange(1, 1000))
            user.save()
            login(request, user, backend='core.custom_auth.custom_auth_backend.CustomAuthBackend')
            return redirect('core:index')
        else:
            context['registration_form'] = form

    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'core/register.html', context)


def login_view(request):
    context = {}

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('core:index'))

    if request.POST:
        form = AuthenticateForm(request.POST)
        email_or_phone = request.POST['email_or_phone']
        password = request.POST['password']
        user = authenticate(email_or_phone=email_or_phone, password=password)
        
        if user:
            login(request, user, backend='core.custom_auth.custom_auth_backend.CustomAuthBackend')
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return HttpResponseRedirect(reverse('core:index'))
    else:
        form = AuthenticateForm()

    context['login_form'] = form
    return render(request, 'core/login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('core:index'))
