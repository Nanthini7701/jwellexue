from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={
            "class": "w-full mt-1 p-2 border rounded-lg focus:ring-yellow-500 focus:border-yellow-500",
            "placeholder": "you@example.com"
        }
    ))

    username = forms.CharField(widget=forms.TextInput(
        attrs={
            "class": "w-full mt-1 p-2 border rounded-lg focus:ring-yellow-500 focus:border-yellow-500",
            "placeholder": "Choose a username"
        }
    ))

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={
            "class": "w-full mt-1 p-2 border rounded-lg focus:ring-yellow-500 focus:border-yellow-500",
            "placeholder": "Create a password"
        }
    ))

    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(
        attrs={
            "class": "w-full mt-1 p-2 border rounded-lg focus:ring-yellow-500 focus:border-yellow-500",
            "placeholder": "Repeat your password"
        }
    ))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email