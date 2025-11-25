from django.db import models
from django.contrib.auth.hashers import make_password 
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.

class Users(models.Model):
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=100, null=False)
    role = models.CharField(max_length=10, default="user")

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

class Books(models.Model):
    book_name = models.CharField(max_length=100, null=False)
    author = models.CharField(max_length=100, null=False)
    thumbnail = models.URLField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)  

    def __str__(self):
        return f"{self.book_name} by {self.author} ({self.quantity} available)"

def default_due_date():
    return timezone.now() + timedelta(days=60)

class BooksBorrowed(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateTimeField(default=default_due_date)

    def __str__(self):
        return f"{self.user_id.name} borrowed {self.book_id.book_name}"
    
class Categories(models.Model):
    category_name = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.category_name
    
class CategoriesPerBook(models.Model):
    book_id = models.ForeignKey(Books, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Categories, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.book_id.book_name} in {self.category_id.category_name}"