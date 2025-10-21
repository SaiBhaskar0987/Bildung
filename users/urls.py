from django.urls import path, include
from . import views

urlpatterns = [
    # Landing / Auth
    path("auth/", views.auth_page, name="auth_page"),

    # Student
    path("student/signup/", views.student_signup, name="student_signup"),
    path("student/login/", views.student_login, name="student_login"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),


    # Instructor
    path("instructor/signup/", views.instructor_signup, name="instructor_signup"),
    path("instructor/login/", views.instructor_login, name="instructor_login"),
    
    # Include all instructor dashboard & course URLs
    path("instructor/", include(("courses.instructor_urls", "instructor"), namespace="instructor")),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),


    # Admin
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # Logout
    path("logout/", views.logout_view, name="logout"),

    # Post-login redirect
    path("post-login/", views.post_login_redirect, name="post_login_redirect"),
]
