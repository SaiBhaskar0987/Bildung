from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("courses/", include("courses.urls")),  # general course views
    path("instructor/", include("courses.instructor_urls", namespace="instructor")),  # instructor dashboard & management
    path("quizzes/", include("quizzes.urls")),
]
