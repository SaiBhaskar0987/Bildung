from django.conf import settings
from django.urls import resolve, reverse, Resolver404
from django.http import HttpResponseRedirect
from importlib import import_module

class SubdomainURLRoutingMiddleware:
    """
    Switches URLConfs based on subdomain:
    student.example.com -> students
    instructor.example.com -> instructor
    admin.example.com -> admin
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0] 
        subdomain = host.split('.')[0]

        if subdomain == 'student':
            request.urlconf = 'users.student_urls'
        elif subdomain == 'instructor':
            request.urlconf = 'users.instructor_urls'
        elif subdomain == 'admin':
            request.urlconf = 'users.admin_urls'
        else:
            request.urlconf = settings.ROOT_URLCONF  

        response = self.get_response(request)
        return response
