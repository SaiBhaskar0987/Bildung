from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from .models import User, EmailVerification
from core import settings as core_settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from .models import LoginHistory

@receiver(post_save, sender=User)
def send_invite_on_creation(sender, instance, created, **kwargs):
    print(f"🚀 New user created: {instance.email}. Sending invitation email...")
    print(instance.is_active)
    print(created)
    if created and not instance.is_active:
        
        verification = EmailVerification.objects.create(user=instance)

        invite_link = f"{core_settings.SITE_URL}/accounts/verify/{instance.role}/{verification.token}/"

        subject = "You have been invited to join Bildung!"
        message = f"""
        Hello {instance.username},

        This is an account for you on the Bildung Platform as a {instance.role}.

        Please click the link below to verify your account and set up your password:
        {invite_link}

        Best regards,
        Bildung Team
        """

        try:
            send_mail(
                subject, 
                message, 
                settings.DEFAULT_FROM_EMAIL, 
                [instance.email], 
                fail_silently=False
            )
            print(f"✅ Invitation sent to {instance.email}")
        except Exception as e:
            print(f"❌ Failed to send invite: {e}")


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
