from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile
from django.contrib.auth import get_user_model

class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name","last_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # Email is used as username
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
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "instructor"
        user.username = self.cleaned_data["email"]  # Email is used as username
        if commit:
            user.save()
        return user 
    
# forms.py
from django import forms
from django.contrib.auth import get_user_model
# Adjust this import path if your models are in a different app
from .models import Profile 

User = get_user_model()

class ProfileForm(forms.ModelForm):
    # Override the resume field to set required=False and add a help message
    resume = forms.FileField(
        required=False, 
        help_text="Only PDF files are allowed.", 
        label="Resume (PDF Only)",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        # Fields managed by this form (only Profile model fields)
        fields = ['about_me', 'phone', 'gender', 'date_of_birth', 'qualification', 'resume']
        widgets = {
            'about_me': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        
        # Check file type only if a new file was uploaded
        if resume:
            if not resume.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed for the resume.")
                
        # Returns the newly uploaded file, or None if no new file was selected.
        return resume

class UserDisplayForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            # Apply 'readonly' attribute to prevent editing
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }