from django.urls import path
from .views import index, logout_user, user_login, user_register, admin_dashboard, user_dashboard, admin_manage, borrow_book, return_book

urlpatterns = [ 
    path("", index, name="index"),
    path("auth/login", user_login, name="auth_login"),
    path("auth/register", user_register, name="auth_register"),
    path("logout", logout_user, name="logout_user"),
    path("dashboard/admin", admin_dashboard, name="admin_dashboard"),
    path("dashboard/user", user_dashboard, name="user_dashboard"),
    path("dashboard/manage", admin_manage, name="admin_manage"),
    path('borrow/<int:book_id>/', borrow_book, name='borrow_book'),
    path("return/<int:borrow_id>/", return_book, name="return_book"),
]
