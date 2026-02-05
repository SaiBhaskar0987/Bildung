from io import BytesIO
from django.http import FileResponse, HttpResponse, JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from courses.utils import check_and_send_reminders
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password 
from django.urls import reverse
from .models import PasswordChangeRequest

from .models import EmailVerification
from .utils import send_verification_email

from .models import User, Profile, LoginHistory, InstructorProfile
from .forms import StudentSignUpForm, InstructorSignUpForm, ProfileForm, UserDisplayForm, InstructorUserReadOnlyForm, InstructorUserForm, InstructorProfileForm
from courses.models import Course, Enrollment, Lecture, LectureProgress, LectureQuestion, LiveClass, LiveClassAttendance, Notification


def auth_page(request):
    return render(request, "users/auth_page.html")


def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = "student"
            user.is_active = False
            user.set_password(form.cleaned_data["password1"])
            user.save()

            Profile.objects.create(user=user)

            verification = EmailVerification.objects.create(user=user)

            send_verification_email(
                request,
                user,
                role="student",
                token=verification.token
            )

            messages.success(
                request,
                "✅ Account created! Please check your email to verify your account."
            )

            return render(request, "users/check_email.html")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = StudentSignUpForm()

    return render(request, "student/student_signup.html", {"form": form})


def student_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'role') and user.role == "student":
                login(request, user)
                record_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("student_dashboard")
            else:
                messages.error(request, "This login is only for students.")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, "student/student_login.html", {"form": form})


@login_required
def student_dashboard(request):
    if request.user.role != "student":
        messages.error(request, "Access denied. Student area only.")
        return redirect("login")
    check_and_send_reminders(request.user)
    all_courses = Course.objects.all()

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by("-created_at")[:5]
    enrolled_course_ids = Enrollment.objects.filter(
        student=request.user
    ).values_list("course_id", flat=True)

    return render(request, "student/student_dashboard.html", {
        "all_courses": all_courses,
        "unread_count": unread_count,
        "unread_notifications": unread_notifications,
        "enrolled_course_ids": enrolled_course_ids,
    })


@login_required
def account_settings(request):
    user = request.user

    if request.method == "POST" and "change_password" in request.POST:
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # 1️⃣ Validate current password
        if not user.check_password(current_password):
            messages.error(request, "❌ Current password is incorrect")
            return redirect("account_settings")

        # 2️⃣ Validate new passwords
        if new_password != confirm_password:
            messages.error(request, "❌ New passwords do not match")
            return redirect("account_settings")

        # 3️⃣ Create password change request (NOT updating password yet)
        password_request = PasswordChangeRequest.objects.create(
            user=user,
            new_password=make_password(new_password)  # hash before storing
        )

        confirm_link = f"http://127.0.0.1:8000/confirm-password/{password_request.token}/"

        # 🔗 PRINT LINK IN TERMINAL
        print("\n🔐 PASSWORD CONFIRMATION LINK")
        print(confirm_link)
        print("⬆️ Click this link to confirm password change\n")

        messages.info(
            request,
            "⚠️ Confirmation link generated. Check VS Code terminal."
        )

        return redirect("account_settings")

    return render(request, "users/account_settings.html")


def confirm_password_change(request, token):
    password_request = get_object_or_404(
        PasswordChangeRequest,
        token=token,
        is_confirmed=False
    )

    if request.method == "POST":
        user = password_request.user

        # ✅ Update password now
        user.password = password_request.new_password
        user.save()

        update_session_auth_hash(request, user)

        password_request.is_confirmed = True
        password_request.save()

        return HttpResponse(
            "<h2>✅ Your password changed successfully</h2>"
        )

    return render(request, "users/confirm_password.html")


@login_required
def profile_view_or_edit(request, mode=None):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    is_editing = (mode == 'edit')

    if request.method == 'POST' and is_editing:
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserDisplayForm(request.POST, instance=request.user) 

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_view') 
        
    else:
        user_form = UserDisplayForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'profile': profile,
        'user_form': user_form,       
        'profile_form': profile_form, 
        'is_editing': is_editing,
    }
    return render(request, 'student/student_profile.html', context)

@login_required
def student_my_activity(request):
    user = request.user
    enrollments = Enrollment.objects.filter(student=user)

    course_progress = []
    for enroll in enrollments:
        course = enroll.course
        lectures = Lecture.objects.filter(module__course=course)
        total_lectures = lectures.count()

        completed = LectureProgress.objects.filter(
            student=user, lecture__in=lectures, completed=True
        ).count()

        percent = round((completed / total_lectures) * 100, 2) if total_lectures > 0 else 0

        course_progress.append({
            "course": course,
            "total_lectures": total_lectures,
            "completed_lectures": completed,
            "progress_percent": percent,
        })

    recent_videos = LectureProgress.objects.filter(
        student=user, completed=True
    ).select_related("lecture", "lecture__module__course").order_by("-updated_at")[:10]

    video_lessons_watched = LectureProgress.objects.filter(
        student=user, completed=True
    ).select_related("lecture", "lecture__module__course").order_by("-updated_at")

    enrolled_course_ids = enrollments.values_list("course_id", flat=True)

    all_live_classes = LiveClass.objects.filter(course_id__in=enrolled_course_ids)

    total_classes = all_live_classes.count()

    attendance_records = (
        LiveClassAttendance.objects
        .filter(user=user, live_class__in=all_live_classes)
        .select_related("live_class", "live_class__course")
    )

    attended_count = attendance_records.exclude(joined_at=None).count()

    attendance_percent = round((attended_count / total_classes) * 100, 2) if total_classes > 0 else 0

    attendance_data = {
        "total_classes": total_classes,
        "classes_attended": attended_count,
        "attendance_percentage": attendance_percent,
        "absences": total_classes - attended_count,
        "live_classes": [
            {
                "title": rec.live_class.title,
                "course": rec.live_class.course.title,
                "date": rec.live_class.date,
                "status": "Joined" if rec.joined_at else "Missed",
                "joined_at": rec.joined_at,
                "duration": f"{rec.duration} mins" if rec.duration else "—",
            }
            for rec in attendance_records
        ]
    }

    login_history = LoginHistory.objects.filter(user=user).order_by("-login_time")[:25]

    qna_activity = (
        LectureQuestion.objects.filter(student=user)
        .select_related("lecture", "lecture__module", "lecture__module__course")
        .prefetch_related("replies__user")
        .order_by("-created_at")
    )

    total_completed = LectureProgress.objects.filter(student=user, completed=True).count()
    total_lectures = Lecture.objects.count()
    overall_progress = (
        round((total_completed / total_lectures) * 100, 2) if total_lectures > 0 else 0
    )

    context = {
        "total_enrolled_courses": enrollments.count(),
        "total_completed_lectures": total_completed,
        "overall_progress": overall_progress,
        "course_progress": course_progress,
        "recent_videos": recent_videos,
        "video_lessons_watched": video_lessons_watched,
        "attendance_data": attendance_data,
        "login_history": login_history,
        "qna_activity": qna_activity,
    }

    return render(request, "student/my_activity.html", context)
    

@login_required
def student_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "student/student_notifications.html", {
        "notifications": notifications
    })


@login_required
def get_recent_notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by("-created_at")[:10]

    data = []
    for n in notes:
        data.append({
            "id": n.id,
            "message": n.message,
            "url": n.url or "",
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%d %b %Y, %I:%M %p")
        })

    unread = Notification.objects.filter(user=request.user, is_read=False).count()

    return JsonResponse({"notifications": data, "unread": unread})


@login_required
def mark_all_notifications(request, notif_id):
    Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
    return JsonResponse({"status": "ok"})

@login_required
def mark_notification(request, notif_id):
    """Mark a single notification as read."""
    Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
    return JsonResponse({"status": "ok"})


# --- Instructor --- #

def instructor_signup(request):
    if request.method == 'POST':
        form = InstructorSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'instructor'
            user.is_active = False

            raw_password = form.cleaned_data.get("password1") or form.cleaned_data.get("password")
            if raw_password:
                user.set_password(raw_password)

            user.save()

            InstructorProfile.objects.create(user=user)

            verification = EmailVerification.objects.create(user=user)

            send_verification_email(
                request,
                user,
                role="instructor",
                token=verification.token
            )

            messages.success(
                request,
                "✅ Account created! Please verify your email to activate your account."
            )

            return render(request, "users/check_email.html")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = InstructorSignUpForm()

    return render(request, 'instructor/instructor_signup.html', {'form': form})


def instructor_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'role') and user.role == "instructor":
                login(request, user)
                record_login(request, user)
                return redirect("instructor_dashboard")
            else:
                messages.error(request, "This login is only for instructors.")
    else:
        form = AuthenticationForm()
    return render(request, "instructor/instructor_login.html", {"form": form})


@login_required
def instructor_dashboard(request):
    check_and_send_reminders(request.user)
    courses = Course.objects.filter(instructor=request.user)
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    total_students = Enrollment.objects.filter(
        course__in=courses
    ).values('student').distinct().count()

    return render(request, 'instructor/instructor_dashboard.html', {
        'courses': courses,
        'total_students': total_students,
        "unread_count": unread_count,
    })


def logout_view(request):
    record_logout(request)
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("auth_page")


def custom_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{request.scheme}://{request.get_host()}/password-reset-confirm/{uid}/{token}/"
            user_role = user.role if hasattr(user, 'role') else 'user'
            subject = f"Password Reset Request - Bildung Platform"
            message = f"""
Hello {user.username},

You're receiving this email because you requested a password reset for your {user_role} account.

Please click the link below to reset your password:
{reset_url}

If you didn't request this reset, please ignore this email.

Thanks,
The Bildung Platform Team
"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return redirect('password_reset_sent')
                
            except Exception as e:
                print(f"Email sending failed: {e}")
                return redirect('password_reset_sent')
            
        except User.DoesNotExist:
            return redirect('password_reset_sent')
    
    return render(request, 'forgot_password.html')

def password_reset_sent(request):
    return render(request, 'password_reset_sent.html')

def custom_password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                if new_password and len(new_password) >= 8:
                    if new_password == confirm_password:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'Your password has been reset successfully! You can now login with your new password.')

                        if hasattr(user, 'role'):
                            if user.role == 'instructor':
                                return redirect('instructor_login')
                            elif user.role == 'student':
                                return redirect('student_login')

                        return redirect('auth_page')
                    else:
                        messages.error(request, 'Passwords do not match.')
                else:
                    messages.error(request, 'Password must be at least 8 characters long.')
            
            return render(request, 'password_reset_confirm.html')
        else:
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('auth_page')
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid reset link.')
        return redirect('auth_page')

@login_required
def instructor_profile_view_or_edit(request, mode=None):

    try:
        profile = request.user.instructor_profile
    except InstructorProfile.DoesNotExist:
        profile = InstructorProfile.objects.create(user=request.user)

    is_editing = (mode == "edit")

    if request.method == "POST" and is_editing:

        user_form = InstructorUserForm(request.POST, instance=request.user)
        profile_form = InstructorProfileForm(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("instructor_profile_view")
    else:
        if is_editing:
            user_form = InstructorUserForm(instance=request.user)
        else:
            user_form = InstructorUserReadOnlyForm(instance=request.user)

        profile_form = InstructorProfileForm(instance=profile)

    context = {
        "profile": profile,
        "user_form": user_form,
        "profile_form": profile_form,
        "is_editing": is_editing,
    }

    return render(request, "instructor/instructor_profile.html", context)


@login_required
def instructor_recent_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    unread_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    data = {
        "unread": unread_count,
        "notifications": [
            {
                "id": n.id,
                "message": n.message,
                "created_at": n.created_at.strftime("%b %d, %I:%M %p"),
                "is_read": n.is_read,
                "url": n.url or "",
            }
            for n in notifications
        ]
    }

    return JsonResponse(data)

@login_required
def instructor_notifications_page(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return render(request, "instructor/instructor_notifications.html", {
        "notifications": notifications,
        "unread_count": unread_count,
    })

@login_required
def instructor_mark_read(request, notif_id):
    Notification.objects.filter(
        id=notif_id,
        user=request.user
    ).update(is_read=True)

    return JsonResponse({"status": "ok"})

@login_required
def instructor_mark_all_read(request):
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({"status": "ok"})


@login_required
def instructor_account_settings(request):
    if request.user.role != "instructor":
        return redirect("login")

    user = request.user

    profile, created = InstructorProfile.objects.get_or_create(user=user)

    if request.method == 'POST':

        if 'update_profile' in request.POST:
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()

            profile.phone = request.POST.get('phone', profile.phone)
            profile.about_me = request.POST.get('about_me', profile.about_me)
            profile.professional_title = request.POST.get('professional_title', profile.professional_title)
            profile.expertise = request.POST.get('expertise', profile.expertise)
            exp = request.POST.get('experience')
            profile.experience = int(exp) if exp.isdigit() else None
            profile.gender = request.POST.get('gender', profile.gender)
            profile.date_of_birth = request.POST.get('date_of_birth', profile.date_of_birth)
            profile.qualification = request.POST.get('qualification', profile.qualification)

            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']

            profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('instructor_account_settings')

        elif 'change_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            if not user.check_password(old_password):
                messages.error(request, "Old password is incorrect.")
                return redirect('instructor_account_settings')

            if new_password1 != new_password2:
                messages.error(request, "New passwords do not match.")
                return redirect('instructor_account_settings')

            if len(new_password1) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect('instructor_account_settings')

            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)

            messages.success(request, "Password changed successfully!")
            return redirect('instructor_account_settings')

        elif 'update_notifications' in request.POST:
            messages.success(request, "Notification preferences updated!")
            return redirect('instructor_account_settings')

    return render(request, 'instructor/instructor_account_settings.html', {
        'user': user,
        'profile': profile,
    })

@login_required(login_url="/auth/")
def admin_dashboard(request):
    if not hasattr(request.user, 'role') or request.user.role != "admin":
        messages.error(request, "Access denied. Admin area only.")
        return redirect("auth_page")
    return render(request, "admin/dashboard.html")

@login_required
def post_login_redirect_view(request):
    user = request.user
    if not hasattr(user, 'role'):
        messages.error(request, "User role not defined.")
        return redirect("auth_page")
    
    if user.role == "student":
        record_login(request, user)
        return redirect("student_dashboard")
    elif user.role == "instructor":
        record_login(request, user)
        return redirect("instructor_dashboard")
    elif user.role == "admin":
        record_login(request, user)
        return redirect("admin_dashboard")
    else:
        return redirect("auth_page")

def google_oauth_entry(request):
    role = request.GET.get('type', '').strip()
    next_url = request.GET.get('next', '/google-redirect/').strip()

    if role:
        request.session['google_role'] = role  

    redirect_url = f"/social-auth/login/google-oauth2/?next={next_url}&prompt=select_account"
    return redirect(redirect_url)


@login_required
def google_login_redirect(request):
    user = request.user
    role_param = request.GET.get('type') or request.session.get('google_role')

    if role_param:
        request.session['google_role'] = role_param

        if role_param == 'instructor' and user.role != 'instructor':
            user.role = 'instructor'
            user.save()
        elif role_param == 'student' and user.role != 'student':
            user.role = 'student'
            user.save()

    if user.role == 'instructor':
        return redirect('instructor_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('auth_page')
    

def record_login(request, user):
    LoginHistory.objects.create(
        user=user,
        login_time=timezone.now(),
        status="Success",
        device=request.META.get('HTTP_USER_AGENT', 'Unknown Device')
    )


def record_logout(request):
    if request.user.is_authenticated:
        last_login_entry = LoginHistory.objects.filter(
            user=request.user,
            logout_time__isnull=True
        ).order_by('-login_time').first()

        if last_login_entry:
            last_login_entry.logout_time = timezone.now()
            last_login_entry.save()

def check_email(request):
    return render(request, "users/check_email.html")


def verify_email(request, role, token):
    verification = get_object_or_404(EmailVerification, token=token)
    user = verification.user
    user.is_active = True
    user.save()
    verification.delete()

    return render(
        request,
        "users/verification_success.html",
        {
            "user": user,
            "role": role
        }
    )
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect


@login_required
def account_settings(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # 1) Validate current password
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("account_settings")

        # 2) Validate new password match
        if new_password != confirm_password:
            messages.error(request, "New password and Confirm password do not match.")
            return redirect("account_settings")

        # 3) Update password
        user.set_password(new_password)
        user.save()

        # 4) Keep user logged in after password change
        update_session_auth_hash(request, user)

        # 5) Send confirmation email
        subject = "Password Changed Successfully"
        message = f"""
Hi {user.get_full_name() or user.username},

Your account password has been changed successfully.

If you did not perform this action, please contact support immediately.

Regards,
Bildung Platform Team
        """.strip()

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(request, "Password updated successfully. Confirmation email generated.")
        return redirect("account_settings")

    return render(request, "account_settings.html")

