from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Roles: student, instructor, admin
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    email = models.EmailField(unique=True)

    # Instructor-specific fields
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ), null=True, blank=True)

    department = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=50, choices=(
        ('professor', 'Professor'),
        ('associate', 'Associate Professor'),
        ('assistant', 'Assistant Professor'),
        ('lecturer', 'Lecturer'),
    ), null=True, blank=True)

    experience = models.CharField(max_length=20, choices=(
        ('0-1', '0-1'),
        ('1-2', '1-2'),
        ('2-3', '2-3'),
    ), null=True, blank=True)

    bio = models.TextField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
