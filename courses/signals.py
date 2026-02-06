from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from courses.models import Course, Enrollment, Notification
from users.models import CourseSearch

User = get_user_model()


@receiver(post_save, sender=Course)
def send_recommendation_notifications(sender, instance, created, **kwargs):
    """
    Notify ONLY when a newly created course matches
    user's explicit preferences (search or enrolled category).
    """
    if not created:
        return

    students = User.objects.filter(role="student")

    for student in students:
        should_notify = False

        recent_searches = CourseSearch.objects.filter(
            user=student
        ).order_by("-searched_at").values_list("keyword", flat=True)[:10]

        for keyword in recent_searches:
            kw = keyword.lower()

            if (
                kw in instance.title.lower()
                or kw in instance.description.lower()
                or kw == instance.category.lower()
            ):
                should_notify = True
                break

        if not should_notify:
            enrolled_categories = Enrollment.objects.filter(
                student=student
            ).values_list("course__category", flat=True)

            if instance.category in enrolled_categories:
                should_notify = True

        if should_notify:
            Notification.objects.create(
                user=student,
                message=f"🔥 New course '{instance.title}' matches your interests",
                url=f"/courses/course/{instance.id}/"
            )
