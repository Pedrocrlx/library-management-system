from django.shortcuts import redirect, render
from .forms import AdminLoginForm
from .models import Books
from django.contrib.auth import authenticate, login
from django.contrib import messages

# Create your views here.


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid credentials or not an admin.")
    else:
        form = AdminLoginForm()

    return render(request, 'admin-login.html', {
        'form': form,
    })


def book_list(request):
    
    books = Books.objects.all()
    title = request.GET.get('title')
    author = request.GET.get('author')

    if title:
        books = books.filter(book_name__icontains=title)
    if author:
        books = books.filter(author__icontains=author)

    return render(request, 'book-list.html', {
        'books': books,
    })
