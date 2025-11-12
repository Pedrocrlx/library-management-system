from django.shortcuts import redirect, render
from .forms import AdminLoginForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Books

# Create your views here.

def login_admin(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin-dashboard')
            else:
                messages.error(request, "Invalid credentials or not an admin.")
    else:
        form = AdminLoginForm()

    return render(request, 'admin-dashboard.html', {
        'form': form,
    })

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            user = authenticate(request, name=name, password=password, email=email)
            login(request, user)
    else:
        form = UserLoginForm()
    
    return render(request, 'index.html', {
        'form': form,
    })

def index(request):
    books = Books.objects.all()
    return render(request, 'index.html', {'books': books})


def logout_admin(request):
    logout(request)
    return redirect('index')
