from django.shortcuts import redirect, render
from django.db.models import Count
from courses.models import Course

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

    popular_categories = (
        Course.objects
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    most_used_category = (
        popular_categories[0]["category"]
        if popular_categories.exists()
        else None
    )

    active_category = selected_category or most_used_category

    total_courses = Course.objects.count()

    if total_courses <= 4:
        popular_courses = Course.objects.order_by("-created_at", "-id")
    else:
        popular_courses = (
            Course.objects
            .filter(category=active_category)
            .order_by("-created_at", "-id")[:4]
            if active_category
            else []
        )

    courses_qs = Course.objects.order_by("-created_at", "-id")

    if selected_category:
        courses_qs = courses_qs.filter(category=selected_category)

    courses = courses_qs[:6]

    context = {
        "popular_categories": popular_categories,
        "popular_courses": popular_courses,
        "courses": courses,
        "selected_category": selected_category,
        "active_category": active_category,
        "most_used_category": most_used_category,
    }

    return render(request, "home/guest_home.html", context)
