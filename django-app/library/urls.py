from django.urls import path
from .views import admin_login, book_list

urlpatterns = [
    path("library/login/", admin_login, name="admin_login"),
    path("library/books/", book_list , name="book_list"),  
]

