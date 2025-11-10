from django.urls import path
from .views import login_admin, logout_admin, index

urlpatterns = [
    path("login_admin/", login_admin, name="admin_login"),
    path("logout_admin/", logout_admin, name="logout_admin"),
    path("", index, name="index"),
]
