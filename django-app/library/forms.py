from django import forms
from .models import Users, Categories


class UserLoginForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class EmailValidationMixin:
    def clean_email(self):
        validate_email = self.cleaned_data.get('email')
        return validate_email.lower()

class PasswordValidationMixin:
    """Mixin to add custom password validation to any form"""

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        if not pwd:
            raise forms.ValidationError("Password is required.")
        if len(pwd) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in pwd):
            raise forms.ValidationError(
                "Password must contain at least one digit.")
        if not any(char.isalpha() for char in pwd):
            raise forms.ValidationError(
                "Password must contain at least one letter.")
        if not any(char.isupper() for char in pwd):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter.")
        return pwd

class UserRegisterForm(PasswordValidationMixin, EmailValidationMixin, forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label="Confirm Password"
    )

    class Meta:
        model = Users
        fields = ['name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
    

class AddBookForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100, required=True)
    author = forms.CharField(label="Author", max_length=100, required=True)
    thumbnail = forms.URLField(label="Thumbnail URL", max_length=200, assume_scheme='https')
    quantity = forms.IntegerField(label="Quantity", min_value=1)

class UpdateBookForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100, required=True)
    author = forms.CharField(label="Author", max_length=100, required=True)
    thumbnail = forms.URLField(label="Thumbnail URL", max_length=200, assume_scheme='https')
    quantity = forms.IntegerField(label="Quantity", min_value=1)
    
    
class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['category_name']
