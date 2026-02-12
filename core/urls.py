from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from home import views as home_views
from django.conf import settings
from django.conf.urls.static import static

from users.views import logout_view, google_login_redirect      


def home(request):
    return HttpResponse("Main Site - Bildung")


urlpatterns = [
    path('admin/', admin.site.urls),
    path("forums/", include("forums.urls")),
    path("chat/", include("chat.urls")),
    path("quizzes/", include("quizzes.urls")),


    path('', home_views.smart_home, name='smart_home'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('google-redirect/', google_login_redirect, name='google_redirect'),

    path("accounts/", include("users.urls")),
    path("", include("users.urls")), 

    path('accounts/logout/', logout_view, name='logout'),
    
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),

    path("api/", include("courses.urls")),

]

SUBDOMAIN_URLCONFS = {
    'instructor': 'courses.instructor_urls',
    'student': 'courses.student_urls',
}

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
