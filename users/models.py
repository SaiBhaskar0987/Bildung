from django.contrib.auth.models import AbstractUser
from django.db import models

bio = models.TextField(blank=True, null=True, default="")


class User(AbstractUser):
    # Roles: student, instructor, admin
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"

from django.db import models
from django.conf import settings
"""
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_instructor': True}  # if you have role flags
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='enrolled_courses',
        blank=True,
        limit_choices_to={'is_student': True}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
"""