from django.urls import path
from .views import index, user_login, user_register, books_list

urlpatterns = [
    path("auth/register", user_register, name="auth_register"),
    path("auth/login", user_login, name="auth_login"),
    path("", index, name="index"),
    path("library/books", books_list, name="list_books"),
]
