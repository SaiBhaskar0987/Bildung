from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import LoginHistory


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LoginHistory.objects.filter(
        user=user,
        logout_time__isnull=True
    ).update(logout_time=timezone.now())

    LoginHistory.objects.create(
        user=user,
        login_time=timezone.now(),
        status="Success",
        device=request.META.get("HTTP_USER_AGENT", "Unknown Device")
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    LoginHistory.objects.filter(
        user=user,
        logout_time__isnull=True
    ).update(logout_time=timezone.now())
