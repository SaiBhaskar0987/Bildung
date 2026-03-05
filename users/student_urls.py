# users/student_urls.py

from django.urls import path, include
from django.contrib.auth import views as auth_views 
from . import views 

urlpatterns = [
    # Student login
    path('login/', views.student_login, name='student_login'), 
    
]

# register courses namespace for student subdomain
urlpatterns += [
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
]
