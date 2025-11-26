# users/student_urls.py

from django.urls import path, include
from django.contrib.auth import views as auth_views 
from . import views 

urlpatterns = [
    # Student login
    path('login/', views.student_login, name='student_login'), 
    
    # Password Reset Paths
    path(
        'password_reset/', 
        auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html'), 
        name='password_reset' 
    ),
    
    path(
        'password_reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
        name='password_reset_done'
    ),
    
    path(
        'reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
        name='password_reset_confirm'
    ),
    
    path(
        'reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
        name='password_reset_complete'
    ),
]

# ✅ ADD THIS — register courses namespace for student subdomain
urlpatterns += [
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
]
