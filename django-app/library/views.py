from urllib import request
from django.shortcuts import redirect, render
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Books, Users

# Create your views here.

# User Registration View
def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            if Users.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email already registered.")
            else:
                user = form.save()
                messages.success(request, f"Registration successful. User ID: {user.id}")
                return redirect('index')
        else:
            # Form validation failed - errors will be displayed in template
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegisterForm()
    
    return render(request, 'user-register.html', {
        'form': form,
    })
# User Login View
def user_login(request):

    if request.method == 'GET':
        form = UserLoginForm(request.GET)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'user-login.html', {
        'form': form,
    })
def logout_user(request):
    logout(request)
    return redirect('index')

def index(request):
    books = [
        {
            "title": "The Great Gatsby",
            "authors": "F. Scott Fitzgerald",
            "thumbnail": "https://covers.openlibrary.org/b/id/7222246-L.jpg",
            "categories": ["Classic", "Fiction"],
        },
        {
            "title": "Atomic Habits",
            "authors": "James Clear",
            "thumbnail": "https://covers.openlibrary.org/b/id/9259256-L.jpg",
            "categories": ["Self-help", "Productivity"],
        },
        {
            "title": "Clean Code",
            "authors": "Robert C. Martin",
            "thumbnail": "https://covers.openlibrary.org/b/id/9644708-L.jpg",
            "categories": ["Programming", "Software Engineering"],
        },
        {
            "title": "The Pragmatic Programmer",
            "authors": "Andrew Hunt, David Thomas",
            "thumbnail": "https://covers.openlibrary.org/b/id/8099251-L.jpg",
            "categories": ["Programming"],
        },
        {
            "title": "The Great Gatsby",
            "authors": "F. Scott Fitzgerald",
            "thumbnail": "https://covers.openlibrary.org/b/id/7222246-L.jpg",
            "categories": ["Classic", "Fiction"],
        },
        {
            "title": "Atomic Habits",
            "authors": "James Clear",
            "thumbnail": "https://covers.openlibrary.org/b/id/9259256-L.jpg",
            "categories": ["Self-help", "Productivity"],
        },
        {
            "title": "Clean Code",
            "authors": "Robert C. Martin",
            "thumbnail": "https://covers.openlibrary.org/b/id/9644708-L.jpg",
            "categories": ["Programming", "Software Engineering"],
        },
        {
            "title": "The Pragmatic Programmer",
            "authors": "Andrew Hunt, David Thomas",
            "thumbnail": "https://covers.openlibrary.org/b/id/8099251-L.jpg",
            "categories": ["Programming"],
        },
        {
            "title": "The Great Gatsby",
            "authors": "F. Scott Fitzgerald",
            "thumbnail": "https://covers.openlibrary.org/b/id/7222246-L.jpg",
            "categories": ["Classic", "Fiction"],
        },
        {
            "title": "Atomic Habits",
            "authors": "James Clear",
            "thumbnail": "https://covers.openlibrary.org/b/id/9259256-L.jpg",
            "categories": ["Self-help", "Productivity"],
        },
        {
            "title": "Clean Code",
            "authors": "Robert C. Martin",
            "thumbnail": "https://covers.openlibrary.org/b/id/9644708-L.jpg",
            "categories": ["Programming", "Software Engineering"],
        },
        {
            "title": "The Pragmatic Programmer",
            "authors": "Andrew Hunt, David Thomas",
            "thumbnail": "https://covers.openlibrary.org/b/id/8099251-L.jpg",
            "categories": ["Programming"],
        }, 
    ]

    query = request.GET.get("q", "").lower()
    if query:
        books = [b for b in books if query in b["title"].lower() or query in b["authors"].lower()]

    return render(request, "index.html", {"books": books})

def books_list(request):
    books = Books.objects.filter(quantity__gt=0)
    return render(request, 'book-list.html', {'books': books})

def admin_dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser == True:
        return redirect('admin_dashboard')
    return render(request, 'admin-dashboard.html')

def admin_logout(request):
    logout(request)
    return redirect('user_login')