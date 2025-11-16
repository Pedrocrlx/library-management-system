from django.urls import path
from .views import index, admin_logout, user_login, user_register, books_list, admin_dashboard

urlpatterns = [
    path("auth/register", user_register, name="auth_register"),
    path("library/logout", admin_logout, name="admin_logout"),
    path("library/dashboard", admin_dashboard, name="admin_dashboard"),
    path("auth/login", user_login, name="auth_login"),
    path("", index, name="index"),
    path("library/books", books_list, name="list_books"),
]
