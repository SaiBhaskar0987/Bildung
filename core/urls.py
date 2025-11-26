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

from django.contrib.auth import views as auth_views    # ✅ Added for logout
from courses import views as course_views  
from users.views import logout_view            # IMPORTANT

# Fallback view for the main domain
def home(request):
    return HttpResponse("Main Site - Bildung")


urlpatterns = [
    path('admin/', admin.site.urls),
    path("forums/", include("forums.urls")),
    path("chat/", include("chat.urls")),

    # Home Page → Use course_views.smart_home instead of home_views.smart_home
    path('', course_views.smart_home, name='smart_home'),

    # User routes
    path("", include("users.urls")),

    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('courses/', include(('courses.urls', 'courses'), namespace='courses'))
]

SUBDOMAIN_URLCONFS = {
    'instructor': 'courses.instructor_urls',
    'student': 'courses.student_urls',
}

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
