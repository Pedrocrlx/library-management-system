from django.contrib import admin
from .models import Books, Users, BooksBorrowed, Categories, CategoriesPerBook
# Register your models here.

admin.site.register(Books)
admin.site.register(Users)
admin.site.register(BooksBorrowed)
admin.site.register(Categories)
admin.site.register(CategoriesPerBook)
