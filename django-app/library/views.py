from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Q #coisa boa
from django.contrib.auth.hashers import check_password
from .forms import UserLoginForm, UserRegisterForm, AddBookForm, AddCategoryForm, UpdateBookForm
from .models import Books, Users, BooksBorrowed, Categories, CategoriesPerBook
from datetime import datetime, timedelta
from django.utils import timezone


# ------------------------------
# USER REGISTRATION
# ------------------------------
def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            # Check email exists
            if Users.objects.filter(email=form.cleaned_data['email']).exists():
                return render(request, 'user-register.html', {'form': form, 'error': "Email already registered."})
            else:
                user = form.save()  
                messages.success(request, f"Registration successful! Welcome, {user.name}.")
                return redirect('auth_login')
        else:
            error_msg = ""
            for field, errors in form.errors.items():
                for error in errors:
                    error_msg += f"{field}: {error} "
            return render(request, 'user-register.html', {'form': form, 'error': error_msg})
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
                return render(request, "user-login.html", {"form": form, "error": "User not found."})


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
                return render(request, "user-login.html", {"form": form, "error": "Incorrect password."})

    else:
        form = UserLoginForm()

    return render(request, "user-login.html", {"form": form})

# ------------------------------
# HOMEPAGE FEED (WITH SEARCH FROM DB)
# ------------------------------
def index(request):
    user_id = request.session.get("user_id")
    user_role = request.session.get("user_role")
    query = request.GET.get("q", "").strip()

    # Get all books
    books_qs = Books.objects.all().prefetch_related('categoriesperbook_set__category_id')

    # Search filter
    if query:
        terms = query.split()
        for term in terms:
            books_qs = books_qs.filter(
                Q(book_name__icontains=term) | 
                Q(author__icontains=term) |
                Q(categoriesperbook__category_id__category_name__icontains=term)
            ).distinct()

    # Prepare data for template
    books = []
    for book in books_qs:
        books.append({
            "id": book.id,
            "title": book.book_name,
            "authors": book.author,
            "thumbnail": book.thumbnail,
            "quantity": book.quantity,
            "categories": [c.category_id.category_name for c in book.categoriesperbook_set.all()]
        })

    # Fetch all categories for the filter
    all_categories = Categories.objects.all()

    # Fetch borrowed books for preview if user is logged in
    borrowed_books = []
    reached_limit = False
    if user_id:
        borrowed_books = BooksBorrowed.objects.filter(user_id=user_id).select_related('book_id')
        reached_limit = borrowed_books.count() >= 3

    return render(request, "index.html", {
        "books": books, 
        "user_id": user_id, 
        "user_role": user_role,
        "all_categories": all_categories,
        "borrowed_books": borrowed_books,
        "reached_limit": reached_limit
    })

# ------------------------------
# USER DASHBOARD
# ------------------------------
def user_dashboard(request):
    user_id = request.session.get("user_id")
    role = request.session.get("user_role")


    if not user_id or role == "admin":
        return redirect("index")

    user = Users.objects.get(id=user_id)

    borrowed_books = user.booksborrowed_set.select_related('book_id').all()

    borrowed_count = borrowed_books.count()
    max_books = 3
    remaining = max_books - borrowed_count

    return render(request, "user-dashboard.html", {
        "user": user,
        "borrowed_books": borrowed_books,
        "borrowed_count": borrowed_count,
        "remaining": remaining,
        "max_books": max_books,
    })


def borrow_book(request, book_id):
    user_id = request.session.get("user_id")
    role = request.session.get("user_role")

    if not user_id or role == "admin":
        return redirect("index")

    user = Users.objects.get(id=user_id)
    book = Books.objects.get(id=book_id)


    if book.quantity <= 0:
        messages.error(request, "This book is out of stock.")
        return redirect("index")


    if BooksBorrowed.objects.filter(user_id=user, book_id=book).exists():
        messages.error(request, "You already borrowed this book.")
        return redirect("index")

    max_books = 3
    borrowed_count = user.booksborrowed_set.count()
    if borrowed_count >= max_books:
        messages.error(request, f"You can only borrow up to {max_books} books at a time.")
        return redirect("index")

    borrowed_date = timezone.now()
    due_date = borrowed_date + timedelta(days=60)  
    BooksBorrowed.objects.create(
        user_id=user,
        book_id=book,
        borrowed_date=borrowed_date,
        due_date=due_date
    )

    book.quantity -= 1
    book.save()

    messages.success(request, f"You borrowed the book: {book.book_name}. It is due on {due_date.strftime('%d-%m-%Y')}.")
    return redirect("user_dashboard")


def return_book(request, borrow_id):
    user_id = request.session.get("user_id")
    role = request.session.get("user_role")

    if not user_id or role == "admin":
        return redirect("index")

    try:
        borrow_entry = BooksBorrowed.objects.get(id=borrow_id, user_id__id=user_id)
    except BooksBorrowed.DoesNotExist:
        messages.error(request, "Borrow entry not found.")
        return redirect("user_dashboard")

    # Increase book quantity
    book = borrow_entry.book_id
    book.quantity += 1
    book.save()

    # Delete borrow entry
    borrow_entry.delete()

    messages.success(request, f"You returned the book: {book.book_name}")
    return redirect("user_dashboard")

# ------------------------------
# ADMIN DASHBOARD
# ------------------------------
def admin_dashboard(request):
    role = request.session.get("user_role")

    if role != "admin":
        return redirect("index")  # Block non-admins

    # Fetch all books for management (needed for stats)
    books = Books.objects.all()
    
    # Calculate stats
    total_titles = books.count()
    total_books_count = sum(book.quantity for book in books)
    
    # Fetch all borrowed books
    borrowed_books = BooksBorrowed.objects.select_related("user_id", "book_id").all()
    borrowed_count = borrowed_books.count()
    
    # Total holdings = Available + Borrowed
    total_holdings = total_books_count + borrowed_count

    return render(request, "admin-dashboard.html", {
        "books": books,
        "borrowed_books": borrowed_books,
        "total_titles": total_titles,
        "total_books_count": total_books_count,
        "borrowed_count": borrowed_count,
        "total_holdings": total_holdings
    })

# ------------------------------
# ADMIN CRUD ADD/DELETE/UPDATE BOOKS
# ------------------------------
def add_category(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New category added successfully.")
            return redirect('admin_manage')  
        else:
            messages.error(request, "Failed to add category.")
    
    return redirect('admin_manage')

def admin_manage(request):
    role = request.session.get("user_role")

    if role != "admin":
        return redirect("index")

    books = Books.objects.all()

    if request.method == "POST":
        form = AddBookForm(request.POST)
        form_category = AddCategoryForm(request.POST)


        if form.is_valid():
            book = Books.objects.create(
                book_name=form.cleaned_data["title"],
                author=form.cleaned_data["author"],
                thumbnail=form.cleaned_data["thumbnail"],
                quantity=form.cleaned_data["quantity"]
            )

            category_fields = [key for key in request.POST.keys() if "category_" in key]
            for field in category_fields:
                category_id = request.POST.get(field)
                if category_id:
                    CategoriesPerBook.objects.create(
                        book_id=book,
                        category_id=Categories.objects.get(id=category_id)
                    )

            messages.success(request, "Book added successfully!")
            return redirect("admin_manage")
        
        if form_category.is_valid() and request.POST.get("book_id"):
            CategoriesPerBook.objects.create(
                book_id=Books.objects.get(id=request.POST.get("book_id")),
                category_id=form_category.cleaned_data["category_id"]
            )
            messages.success(request, "Category assigned to book successfully!")
            return redirect("admin_manage")

    else:
        form = AddBookForm()
        form_category = AddCategoryForm() 

    all_categories = Categories.objects.all()

    return render(request, "admin-manage.html", {
        "form": form,
        "form_category": form_category,
        "books": books,
        "all_categories": all_categories
    })


def admin_delete_book(request, book_id):
    role = request.session.get("user_role")

    if role != "admin":
        return redirect("index")  

    try:
        book = Books.objects.get(id=book_id)
        book.delete()
        messages.success(request, "Book deleted successfully!")
    except Books.DoesNotExist:
        messages.error(request, "Book not found.")

    return redirect("admin_manage")


def update_book(request, book_id):
    role = request.session.get("user_role")

    if role != "admin":
        return redirect("index")  

    try:
        book = Books.objects.get(id=book_id)
    except Books.DoesNotExist:
        messages.error(request, "Book not found.")
        return redirect("admin_manage")

    if request.method == "POST":
        form = UpdateBookForm(request.POST)

        if form.is_valid():
            book.book_name = form.cleaned_data["title"]
            book.author = form.cleaned_data["author"]
            book.thumbnail = form.cleaned_data["thumbnail"]
            book.quantity = form.cleaned_data["quantity"]
            book.save()
            messages.success(request, "Book updated successfully!")
            return redirect("admin_manage")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect("admin_manage")
    else:
        form = UpdateBookForm(initial={
            "title": book.book_name,
            "author": book.author,
            "thumbnail": book.thumbnail,
            "quantity": book.quantity
        })

    return render(request, "admin-update-book.html", {"form": form, "book": book})

# ------------------------------
# ADMIN CRUD ADD/UPDATE/DELETE BOOKS
# ------------------------------

def auth_logout(request):
    request.session.flush()  
    return redirect('index')