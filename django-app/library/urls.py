from django.urls import path
from .views import index, logout_user, user_login, user_register, admin_dashboard, user_dashboard, admin_manage

urlpatterns = [ 
    path("", index, name="index"),
    path("auth/login", user_login, name="auth_login"),
    path("auth/register", user_register, name="auth_register"),
    path("logout", logout_user, name="logout_user"),
    path("dashboard/admin", admin_dashboard, name="admin_dashboard"),
    path("dashboard/user", user_dashboard, name="user_dashboard"),
    path("dashboard/manage", admin_manage, name="admin_manage"),
]
