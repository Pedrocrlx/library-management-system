import pytest
from django.test import Client
from django.urls import reverse
from library.models import Users, Books, BooksBorrowed

@pytest.mark.django_db
class TestIntegration:
    def setup_method(self):
        self.client = Client()
        # Create a test user
        self.user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Password123", 
            "role": "user"
        }
        self.user = Users.objects.create(
            name=self.user_data["name"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            role=self.user_data["role"]
        )
        
        # Create a test book
        self.book = Books.objects.create(
            book_name="Test Book",
            author="Test Author",
            quantity=5
        )

    def test_public_access(self):
        """Test that the home page is accessible and lists books."""
        response = self.client.get(reverse('index'))
        assert response.status_code == 200
        assert "Test Book" in response.content.decode()

    def test_search_functionality(self):
        """Test searching for books by title and author."""
        # Create another book for contrast
        Books.objects.create(book_name="Another Book", author="Another Author", quantity=3)
        
        # Search by title
        response = self.client.get(reverse('index') + '?q=Test')
        content = response.content.decode()
        assert "Test Book" in content
        assert "Another Book" not in content

        # Search by author
        response = self.client.get(reverse('index') + '?q=Another')
        content = response.content.decode()
        assert "Another Book" in content
        assert "Test Book" not in content

    def test_authentication_flow(self):
        """Test registration, login, and logout."""
        # Test Register
        register_data = {
            "name": "New User",
            "email": "new@example.com",
            "password": "Password123", 
            "confirm_password": "Password123",
            "role": "user"
        }
        response = self.client.post(reverse('auth_register'), register_data)
        assert response.status_code == 302  
        assert Users.objects.filter(email="new@example.com").exists()

        # Test Login
        login_data = {
            "name": "New User", 
            "password": "Password123"
        }
        response = self.client.post(reverse('auth_login'), login_data)
        assert response.status_code == 302  # Should redirect to dashboard
        
        # Check session
        session = self.client.session
        assert 'user_id' in session

        # Test Logout
        response = self.client.get(reverse('auth_logout'))
        assert response.status_code == 302 
        assert 'user_id' not in self.client.session

    def test_login_failure(self):
        """Test login with wrong credentials."""
        login_data = {
            "name": self.user_data["name"],
            "password": "WrongPassword"
        }
        response = self.client.post(reverse('auth_login'), login_data)
        assert response.status_code == 200 # Should stay on page
        assert "Incorrect password" in response.content.decode()

        login_data["name"] = "NonExistentUser"
        response = self.client.post(reverse('auth_login'), login_data)
        assert response.status_code == 200
        assert "User not found" in response.content.decode()

    def test_dashboard_access(self):
        """Test that dashboard is only accessible to logged-in users."""
        # Anonymous access should redirect
        self.client.logout()
        response = self.client.get(reverse('user_dashboard'))
        assert response.status_code == 302

        # Logged in access
        login_data = {"name": self.user_data["name"], "password": self.user_data["password"]} # Use name
        self.client.post(reverse('auth_login'), login_data)
        
        response = self.client.get(reverse('user_dashboard'))
        assert response.status_code == 200

    def test_borrowing_flow(self):
        """Test borrowing and returning a book."""
        # Login first
        login_data = {"name": self.user_data["name"], "password": self.user_data["password"]} # Use name
        self.client.post(reverse('auth_login'), login_data)

        # Borrow book
        response = self.client.get(reverse('borrow_book', args=[self.book.id]))
        assert response.status_code == 302 # Redirect after borrow
        
        # Verify DB
        assert BooksBorrowed.objects.filter(user_id=self.user, book_id=self.book).exists()
        
        # Refresh book to check quantity
        self.book.refresh_from_db()
        assert self.book.quantity == 4

        # Try to borrow same book again
        response = self.client.get(reverse('borrow_book', args=[self.book.id]))
        assert response.status_code == 302
        # Should verify message but for now just check DB didn't create duplicate
        assert BooksBorrowed.objects.filter(user_id=self.user, book_id=self.book).count() == 1

        # Return book
        borrow_entry = BooksBorrowed.objects.get(user_id=self.user, book_id=self.book)
        response = self.client.get(reverse('return_book', args=[borrow_entry.id]))
        assert response.status_code == 302
        
        # Verify DB
        assert not BooksBorrowed.objects.filter(id=borrow_entry.id).exists()
        
        # Refresh book to check quantity
        self.book.refresh_from_db()
        assert self.book.quantity == 5

    def test_borrowing_unauthenticated(self):
        """Test that unauthenticated users cannot borrow books."""
        self.client.logout()
        response = self.client.get(reverse('borrow_book', args=[self.book.id]))
        assert response.status_code == 302 # Redirect to index or login
        
        # Verify DB unchanged
        assert not BooksBorrowed.objects.filter(user_id=self.user, book_id=self.book).exists()

    def test_admin_operations(self):
        """Test admin capabilities: create, update, delete books."""
        # Create admin user
        admin_user = Users.objects.create(
            name="Admin User",
            email="admin@example.com",
            password="AdminPassword123",
            role="admin"
        )
        
        # Login as admin
        login_data = {"name": "Admin User", "password": "AdminPassword123"}
        self.client.post(reverse('auth_login'), login_data)

        # Create Book
        new_book_data = {
            "title": "New Admin Book",
            "author": "Admin Author",
            "thumbnail": "http://example.com/image.jpg",
            "quantity": 10
        }
        response = self.client.post(reverse('admin_manage'), new_book_data)
        assert response.status_code == 302
        assert Books.objects.filter(book_name="New Admin Book").exists()
        new_book = Books.objects.get(book_name="New Admin Book")

        # Update Book
        update_data = {
            "title": "Updated Admin Book",
            "author": "Admin Author",
            "thumbnail": "http://example.com/image.jpg",
            "quantity": 15
        }
        response = self.client.post(reverse('update_book', args=[new_book.id]), update_data)
        assert response.status_code == 302
        new_book.refresh_from_db()
        assert new_book.book_name == "Updated Admin Book"
        assert new_book.quantity == 15

        # Delete Book
        response = self.client.get(reverse('admin_delete_book', args=[new_book.id]))
        assert response.status_code == 302
        assert not Books.objects.filter(id=new_book.id).exists()

    def test_permissions(self):
        """Test that normal users cannot access admin endpoints."""
        # Login as normal user
        login_data = {"name": self.user_data["name"], "password": self.user_data["password"]}
        self.client.post(reverse('auth_login'), login_data)

        # Try to access admin dashboard
        response = self.client.get(reverse('admin_dashboard'))
        assert response.status_code == 302 # Should redirect

        # Try to access admin manage
        response = self.client.get(reverse('admin_manage'))
        assert response.status_code == 302

        # Try to delete a book
        response = self.client.get(reverse('admin_delete_book', args=[self.book.id]))
        assert response.status_code == 302
        assert Books.objects.filter(id=self.book.id).exists() # Book should still exist
