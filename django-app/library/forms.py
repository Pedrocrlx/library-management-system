from django import forms

class AdminLoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class BookListForm(forms.Form):
    title = forms.CharField(label="Title", max_length=200, required=False)
    author = forms.CharField(label="Author", max_length=100, required=False)
    categories = forms.CharField(label="Genre", max_length=50, required=False)

    