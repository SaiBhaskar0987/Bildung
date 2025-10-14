from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("courses/", include("courses.urls")),  # general course views
    path("instructor/", include("courses.instructor_urls", namespace="instructor")),  # instructor dashboard & management
    path("quizzes/", include("quizzes.urls")),
]
# urls.py

from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    # ... your other URLs ...

    # The Password Reset URL is defined here
    path(
        'password_reset/', 
        auth_views.PasswordResetView.as_view(template_name='students/password_reset_form.html'), 
        name='password_reset' # <-- The name matching the HTML link!
    ),
    
    # You must also define the other 3 password reset paths for the flow to complete
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(...), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(...), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(...), name='password_reset_complete'),
]