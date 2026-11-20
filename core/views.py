from django.shortcuts import render, redirect


def login_view(request):
    return render(request, 'core/login.html', {"logined": False})


def signup_view(request):
    return render(request, 'core/signup.html', {"logined": False})


def profile_view(request):
    return render(request, 'core/profile.html', {"logined": True})


def logout_view(request):
    return redirect('login');
