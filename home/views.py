from django.shortcuts import redirect, render
from courses.models import Course

def smart_home(request):
    courses = Course.objects.all()[:6]
    if request.user.is_authenticated:
        if request.user.role == "student":
            return redirect('student_dashboard')
        elif request.user.role == "instructor":
            return redirect('instructor:instructor_dashboard')
        elif request.user.role == "admin":
            return redirect('admin_dashboard')
    # if not logged in → show guest home
    return render(request, "home/guest_home.html", {"courses": courses})