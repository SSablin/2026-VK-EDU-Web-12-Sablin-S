from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from core.forms import LoginForm, RegisterForm


def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=login, password=password)
            if user is not None:
                auth.login(request, user)
                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect(reverse('index'))
            form.add_error(None, "Invalid login or password.")
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {"form": form, "next": next_url})


def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = RegisterForm()

    return render(request, 'core/signup.html', {"form": form})


@login_required(login_url='login')
def profile_view(request):
    return render(request, 'core/profile.html', {"logined": True})


def logout_view(request):
    auth.logout(request)
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
        referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect(reverse('index'))
