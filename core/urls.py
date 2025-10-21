"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from home import views as home_views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


# Fallback view for the main domain
def home(request):
    return HttpResponse("Main Site - Bildung")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("forums/", include("forums.urls")),
    path("chat/", include("chat.urls")),

    # Main site root
    path('', home_views.guest_home, name='guest_home'),

    # Include all user-related routes (signup, login, dashboards)
    path("", include("users.urls")),
    path('', include('courses.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # For password reset and other auth views
]

SUBDOMAIN_URLCONFS = {
    'instructor': 'courses.instructor_urls',
    'student': 'courses.student_urls',  # you'll create later
}

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
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