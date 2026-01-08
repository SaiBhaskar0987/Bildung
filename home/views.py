from django.shortcuts import redirect, render
from courses.models import Course
from django.db.models import Count

def smart_home(request):

    if request.user.is_authenticated:
        role_redirects = {
            "student": "student_dashboard",
            "instructor": "instructor_dashboard",
            "admin": "admin_dashboard",
        }
        dashboard = role_redirects.get(request.user.role)
        if dashboard:
            return redirect(dashboard)

    popular_categories = (
        Course.objects
        .values("category")
        .annotate(course_count=Count("id"))
        .order_by("-course_count")
    )

    popular_courses = (
        Course.objects
        .annotate(enroll_count=Count("enrollments"))  
        .order_by("-enroll_count", "-created_at")[:4]
    )

    selected_category = request.GET.get("category")

    courses_qs = Course.objects.order_by("-created_at", "-id")

    if selected_category:
        courses_qs = courses_qs.filter(category=selected_category)

    courses = courses_qs[:6]

    context = {
        "popular_categories": popular_categories,
        "popular_courses": popular_courses,
        "courses": courses,
        "selected_category": selected_category,
    }

    return render(request, "home/guest_home.html", context)
