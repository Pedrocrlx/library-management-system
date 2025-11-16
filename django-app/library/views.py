from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Q #coisa boa
from django.contrib.auth.hashers import check_password
from .forms import UserLoginForm, UserRegisterForm
from .models import Books, Users, BooksBorrowed


# ------------------------------
# USER REGISTRATION
# ------------------------------
def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            # Check email exists
            if Users.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, "Email already registered.")
            else:
                user = form.save()  
                messages.success(request, f"Registration successful! Welcome, {user.name}.")
                return redirect('auth_login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegisterForm()

    return render(request, 'user-register.html', {'form': form})



# ------------------------------
# USER LOGIN
# ------------------------------
def user_login(request):

    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            password = form.cleaned_data["password"]

            try:
                user = Users.objects.get(name=name)
            except Users.DoesNotExist:
                messages.error(request, "User not found.")
                return render(request, "user-login.html", {"form": form})


            if check_password(password, user.password):

                request.session["user_id"] = user.id
                request.session["user_name"] = user.name
                request.session["user_role"] = user.role  

                # Redirect by role
                if user.role == "admin":
                    return redirect("admin_dashboard")
                else:
                    return redirect("index")

            else:
                messages.error(request, "Incorrect password.")

    else:
        form = UserLoginForm()

    return render(request, "user-login.html", {"form": form})



# ------------------------------
# LOGOUT
# ------------------------------
def logout_user(request):
    request.session.flush()  
    return redirect('index')


# ------------------------------
# HOMEPAGE FEED (WITH SEARCH FROM DB)
# ------------------------------
def index(request):
    query = request.GET.get("q", "").strip()

    # Get books with quantity > 0
    books_qs = Books.objects.filter(quantity__gt=0).prefetch_related('categoriesperbook_set__category_id')

    # Search filter
    if query:
        books_qs = books_qs.filter(
            Q(book_name__icontains=query) | 
            Q(author__icontains=query) |
            Q(categoriesperbook__category_id__category_name__icontains=query)
        ).distinct()

    # Prepare data for template
    books = []
    for book in books_qs:
        books.append({
            "title": book.book_name,
            "authors": book.author,
            "thumbnail": book.thumbnail,
            "categories": [c.category_id.category_name for c in book.categoriesperbook_set.all()]
        })

    return render(request, "index.html", {"books": books})

# ------------------------------
# USER DASHBOARD
# ------------------------------
def user_dashboard(request):
    user_id = request.session.get("user_id")
    role = request.session.get("user_role")

    # Block non-logged in or admin users
    if not user_id or role == "admin":
        return redirect("index")

    user = Users.objects.get(id=user_id)

    # Fetch books borrowed by this user
    borrowed_books = user.booksborrowed_set.all()

    return render(request, "user-dashboard.html", {
        "user": user,
        "borrowed_books": borrowed_books
    })


# ------------------------------
# ADMIN DASHBOARD
# ------------------------------
def admin_dashboard(request):
    role = request.session.get("user_role")

    if role != "admin":
        return redirect("index")  # Block non-admins

    # Fetch all books for management
    books = Books.objects.all()

    # Optional: fetch all borrowed books for overview
    borrowed_books = BooksBorrowed.objects.select_related("user_id", "book_id").all()

    return render(request, "admin-dashboard.html", {
        "books": books,
        "borrowed_books": borrowed_books
    })



def logout_user(request):
    request.session.flush()  
    return redirect('index')