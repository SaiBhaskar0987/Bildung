# users/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def instructor_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('instructor_login')  # fixed here
        if getattr(request.user, 'role', None) != 'instructor':
            messages.error(request, "You must be an instructor to access this page.")
            return redirect('student_dashboard')  # keep students away
        return view_func(request, *args, **kwargs)
    return _wrapped
