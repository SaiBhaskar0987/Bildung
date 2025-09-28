from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "student"
        if commit:
            user.save()
        return user


class InstructorSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "date_of_birth",
            "gender",
            "department",
            "position",
            "experience",
            "bio",
        ]
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "instructor"
        if commit:
            user.save()
        return user

