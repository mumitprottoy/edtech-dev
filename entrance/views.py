from django.shortcuts import render, redirect
from django.contrib.auth import logout as logout_user
from . import operations
from utils import global_context


def signup(): pass

def login(request):
    context = global_context.Context.get_context()
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if operations.login_user(
            request, username, password):
            return redirect('home')
    return render(request, 'entrance/login.html', context)

def logout(request):
    logout_user(request)
    return redirect('login')