from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_verification_email(request, user, role, token):
    verify_url = request.build_absolute_uri(
        f"/accounts/verify/{role}/{token}/"
    )

    html_message = render_to_string(
        "users/verify_email.html",
        {
            "user": user,
            "verify_url": verify_url
        }
    )

    email = EmailMessage(
        subject="Verify your email - Bildung",
        body=html_message,
        to=[user.email],
    )
    email.content_subtype = "html"
    email.send()
