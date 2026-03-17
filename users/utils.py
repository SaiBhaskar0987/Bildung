from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from django.shortcuts import redirect
from django.contrib import messages


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
        subject="Verify your email - Speshway",
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.content_subtype = "html"
    email.send()
    

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "admin":
            messages.error(request, "Admin access required.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper