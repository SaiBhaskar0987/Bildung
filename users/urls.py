from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Landing / Auth
    path("auth/", views.auth_page, name="auth_page"),

    # Student
    path("student/signup/", views.student_signup, name="student_signup"),
    path("student/login/", views.student_login, name="student_login"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    
    # Student course-related URLs (namespaced)
    path("student/", include(("courses.student_urls", "student_courses"), namespace="student_courses")),
    path('profile/', views.profile_view_or_edit, name='profile_view'),
    path('profile/edit/', views.profile_view_or_edit, {'mode': 'edit'}, name='profile_edit'),

    # --- CUSTOM PASSWORD RESET URLs ---
    path('forgot-password/', views.custom_password_reset, name='forgot_password'),
    path('password-reset-sent/', views.password_reset_sent, name='password_reset_sent'),
    path('password-reset-confirm/<uidb64>/<token>/', views.custom_password_reset_confirm, name='password_reset_confirm'),
    path("student/login/", views.student_login, name="student_login"),
    # -----------------------------------------------------------------

    # Instructor
    path("instructor/signup/", views.instructor_signup, name="instructor_signup"),
    path("instructor/login/", views.instructor_login, name="instructor_login"),

    # Include all instructor dashboard & course URLs
    path("instructor/", include(("courses.instructor_urls", "instructor"), namespace="instructor")),

    # Admin
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # Logout
    path("logout/", views.logout_view, name="logout_view"),

    # Post-login redirect
    path("post-login/", views.post_login_redirect_view, name="post_login_redirect"),

    # Google OAuth Routes
    path("social-auth/", include("social_django.urls", namespace="social")),
    path("google/login/", views.google_oauth_entry, name="google_oauth_entry"),
    path("google-redirect/", views.google_login_redirect, name="google_login_redirect"),
]