from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Q #coisa boa
from django.contrib.auth.hashers import check_password
from .forms import UserLoginForm, UserRegisterForm, AddBookForm
from .models import Books, Users, BooksBorrowed
from datetime import datetime, timedelta


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
# HOMEPAGE FEED (WITH SEARCH FROM DB)
# ------------------------------
def index(request):
    user_id = request.session.get("user_id")
    user_role = request.session.get("user_role")
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
            "id": book.id,
            "title": book.book_name,
            "authors": book.author,
            "thumbnail": book.thumbnail,
            "categories": [c.category_id.category_name for c in book.categoriesperbook_set.all()]
        })

    return render(request, "index.html", {"books": books, "user_id": user_id, "user_role": user_role})

# ------------------------------
# USER DASHBOARD
# ------------------------------
def user_dashboard(request):
    user_id = request.session.get("user_id")
    role = request.session.get("user_role")

    # Bloquear não-logged ou admin
    if not user_id or role == "admin":
        return redirect("index")

    user = Users.objects.get(id=user_id)

    # Livros que o usuário pegou
    borrowed_books = user.booksborrowed_set.select_related('book_id').all()

    # Quantidade de livros já pegos
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

    # Verificar stock
    if book.quantity <= 0:
        messages.error(request, "This book is out of stock.")
        return redirect("index")

    # Verificar se já pegou o mesmo livro
    if BooksBorrowed.objects.filter(user_id=user, book_id=book).exists():
        messages.error(request, "You already borrowed this book.")
        return redirect("index")

    # Limite máximo de livros
    max_books = 3
    borrowed_count = user.booksborrowed_set.count()
    if borrowed_count >= max_books:
        messages.error(request, f"You can only borrow up to {max_books} books at a time.")
        return redirect("index")

    # Criar borrow com limite de 2 meses
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=60)  # 2 meses aproximados
    BooksBorrowed.objects.create(
        user_id=user,
        book_id=book,
        borrow_date=borrow_date,
        due_date=due_date
    )

    # Reduzir quantidade
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

    # Fetch all books for management
    books = Books.objects.all()

    # Optional: fetch all borrowed books for overview
    borrowed_books = BooksBorrowed.objects.select_related("user_id", "book_id").all()

    return render(request, "admin-dashboard.html", {
        "books": books,
        "borrowed_books": borrowed_books
    })


def admin_manage(request):
    role = request.session.get("user_role")

    if role != "admin":
        return redirect("index")  # Block non-admins

    books = Books.objects.all()

    if request.method == "POST":
        form = AddBookForm(request.POST)

        if form.is_valid():
            Books.objects.create(
                book_name=form.cleaned_data["title"],
                author=form.cleaned_data["author"],
                thumbnail=form.cleaned_data["thumbnail"],
                quantity=form.cleaned_data["quantity"]
            )
            messages.success(request, "Book added successfully!")
            return redirect("admin_manage")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AddBookForm()

    return render(request, "admin-manage.html", {"form": form, "books": books})

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


def logout_user(request):
    request.session.flush()  
    return redirect('index')