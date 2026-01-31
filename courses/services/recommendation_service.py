from django.db.models import Q, Count
from courses.models import Course
from users.models import CourseSearch
from courses.models import Enrollment


def get_recommended_courses(user):
    """
    Return ALL relevant courses based on user preferences
    (search + enrolled categories), ordered by popularity.
    """

    enrolled_course_ids = Enrollment.objects.filter(
        student=user
    ).values_list("course_id", flat=True)

    enrolled_categories = set(
        Enrollment.objects.filter(student=user)
        .values_list("course__category", flat=True)
    )

    recent_searches = CourseSearch.objects.filter(
        user=user
    ).order_by("-searched_at").values_list("keyword", flat=True)[:10]

    preference_q = Q()
    category_intent = set()

    all_categories = set(
        Course.objects.values_list("category", flat=True)
    )

    for keyword in set(recent_searches):
        preference_q |= Q(title__icontains=keyword)
        preference_q |= Q(description__icontains=keyword)

        for category in all_categories:
            if keyword.lower() == category.lower():
                category_intent.add(category)
                preference_q |= Q(category__iexact=category)

    preferred_categories = enrolled_categories.union(category_intent)

    if preferred_categories:
        preference_q |= Q(category__in=preferred_categories)

    return (
        Course.objects.filter(preference_q)
        .exclude(id__in=enrolled_course_ids)
        .annotate(enroll_count=Count("enrollments"))
        .order_by("-enroll_count", "-created_at")
        .distinct()
    )
