from django.urls import path
from .views import index, auth_logout, update_book, user_login, user_register, admin_dashboard, user_dashboard, admin_manage, borrow_book, return_book, admin_delete_book, add_category

urlpatterns = [ 
    path("", index, name="index"),
    path("auth/login", user_login, name="auth_login"),
    path("auth/register", user_register, name="auth_register"),
    path("logout", auth_logout, name="auth_logout"),
    path("dashboard/admin", admin_dashboard, name="admin_dashboard"),
    path("dashboard/user", user_dashboard, name="user_dashboard"),
    path("dashboard/manage", admin_manage, name="admin_manage"),
    path('update_book/<int:book_id>/', update_book, name='update_book'),
    path('borrow/<int:book_id>/', borrow_book, name='borrow_book'),
    path("return/<int:borrow_id>/", return_book, name="return_book"),
    path("dashboard/admin/<int:book_id>/delete", admin_delete_book, name="admin_delete_book"),
    path('add-category/', add_category, name='add_category'),
]