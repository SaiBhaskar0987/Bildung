from django.shortcuts import redirect, render
from django.db.models import Count
from courses.models import Course

from django.db.models import Count
from django.shortcuts import redirect, render

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

    selected_category = request.GET.get("category")

    approved_courses = Course.objects.filter(
        status="approved",
        is_published=True
    )

    popular_categories = (
        approved_courses
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    popular_courses = (
        approved_courses
        .annotate(popularity=Count("enrollments"))
        .order_by("-popularity", "-created_at")[:4]
    )

    courses = approved_courses.order_by("-created_at")

    if selected_category:
        courses = courses.filter(category=selected_category)

    context = {
        "popular_categories": popular_categories,
        "popular_courses": popular_courses,
        "courses": courses,
        "selected_category": selected_category,
    }

    return render(request, "home/guest_home.html", context)