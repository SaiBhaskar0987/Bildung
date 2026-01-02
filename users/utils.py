from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_verification_email(request, user, role, token):
    verify_url = request.build_absolute_uri(
        f"/accounts/verify/{role}/{token}/"
    )

    print("\n" + "=" * 70)
    print("📧 SENDING VERIFICATION EMAIL")
    print(f"👤 User: {user.email}")
    print(f"🧑 Role: {role}")
    print(f"🔗 Verification URL:\n{verify_url}")
    print("=" * 70 + "\n")


    html_message = render_to_string(
        "users/verify_email.html",
        {
            "user": user,
            "verify_url": verify_url,
        }
    )

    email = EmailMessage(
        subject="Verify your email - Bildung",
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.content_subtype = "html"
    email.send()
