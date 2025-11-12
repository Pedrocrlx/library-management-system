from django import forms
from .models import Users

class UserLoginForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['name', 'password', 'email']
        widgets = {
            'password': forms.PasswordInput(),
        }
