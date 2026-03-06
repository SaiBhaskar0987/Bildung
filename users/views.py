from datetime import timedelta

from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from courses.utils import check_and_send_reminders
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q, Avg, Count, Sum
from django.contrib.admin.views.decorators import staff_member_required

from quizzes.models import QuizResult
from .models import EmailVerification, NotificationSettings
from .utils import send_verification_email
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.hashers import make_password 
from .models import PasswordChangeRequest
from courses.services.recommendation_service import get_recommended_courses

from .models import User, Profile, LoginHistory, InstructorProfile
from .forms import StudentSignUpForm, InstructorSignUpForm, ProfileForm, UserDisplayForm, InstructorUserReadOnlyForm, InstructorUserForm, InstructorProfileForm
from courses.models import Certificate, Course, CourseReview, Enrollment, Feedback, Lecture, LectureProgress, LectureQuestion, LiveClass, LiveClassAttendance, Notification

def auth_page(request):
    return render(request, "users/login_page.html")

def signup_page(request):
    return render(request, "users/signup_page.html", {
        "student_form": StudentSignUpForm(),
        "instructor_form": InstructorSignUpForm(),
    })


def student_signup(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            Profile.objects.create(user=user)

            verification, _ = EmailVerification.objects.get_or_create(user=user)

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

            return render(request, "users/signup_page.html", {
                "student_form": form,
                "instructor_form": InstructorSignUpForm(),
            })

    return redirect("signup_page")

def student_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'role') and user.role == "student":
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("student_dashboard")
            else:
                messages.error(request, "This login is only for students.")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    form.fields["username"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Enter your email"
    })
    form.fields["password"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Enter your password",
        "id": "id_password"
    })
    return render(request, "student/student_login.html", {"form": form})

@login_required
def student_dashboard(request):
    user = request.user

    if user.role != "student":
        messages.error(request, "Access denied.")
        return redirect("auth_page")

    enrollments = Enrollment.objects.filter(
        student=user
    ).select_related("course")

    enrolled_course_ids = enrollments.values_list("course_id", flat=True)
    enrolled_courses_count = enrollments.count()

    certificates_count = Certificate.objects.filter(
        student=user
    ).count()

    total_lectures = Lecture.objects.filter(
        module__course_id__in=enrolled_course_ids
    ).count()

    completed_lectures = LectureProgress.objects.filter(
        student=user,
        completed=True,
        lecture__module__course_id__in=enrolled_course_ids
    ).count()

    if total_lectures > 0:
        average_progress = round((completed_lectures / total_lectures) * 100)
    else:
        average_progress = 0

    unread_notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by("-created_at")[:5]

    unread_count = unread_notifications.count()

    recommended_courses = get_recommended_courses(user)

    all_courses = (
        Course.objects
        .filter(
            Q(status="approved", is_published=True) |
            Q(id__in=enrolled_course_ids)
        )
        .annotate(popularity=Count("enrollments"))
        .select_related("instructor")
        .order_by("-popularity", "-created_at")
    )

    popular_categories = (
        Course.objects
        .filter(status="approved", is_published=True)
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total")[:6]
    )

    dashboard_stats = [
        {
            "icon": "fas fa-book-open",
            "value": enrolled_courses_count,
            "label": "Enrolled Courses",
        },
        {
            "icon": "fas fa-certificate",
            "value": certificates_count,
            "label": "Certificates Earned",
        },
        {
            "icon": "fas fa-chart-line",
            "value": f"{average_progress}%",
            "label": "Learning Progress",
        },
    ]

    context = {
        "all_courses": all_courses,
        "recommended_courses": recommended_courses,
        "enrolled_course_ids": enrolled_course_ids,
        "unread_count": unread_count,
        "unread_notifications": unread_notifications,
        "popular_categories": popular_categories,
        "dashboard_stats": dashboard_stats,
    }

    return render(request, "student/student_dashboard.html", context)


@login_required
def account_settings(request):
    user = request.user
    step = request.GET.get("step", "form")

    notification_settings, created = NotificationSettings.objects.get_or_create(user=user)

    if request.method == "POST":

        if "change_password" in request.POST:

            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect")
                return redirect("account_settings")

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match")
                return redirect("account_settings")

            if len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters")
                return redirect("account_settings")

            PasswordChangeRequest.objects.filter(
                user=user,
                is_confirmed=False
            ).delete()

            password_request = PasswordChangeRequest.objects.create(
                user=user,
                new_password=make_password(new_password)
            )

            confirm_link = request.build_absolute_uri(
                reverse("confirm_password_change",
                        args=[str(password_request.token)])
            )

            send_mail(
                subject="Confirm Your Password Change - Speshway",
                message=f"""
Hello {user.first_name},

Click the link below to confirm your password change:

{confirm_link}

This link will expire in 15 minutes.

If this wasn't you, ignore this email.
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return redirect(f"{reverse('account_settings')}?step=email_sent")

        elif "update_notifications" in request.POST:

            notification_settings.email_notifications = bool(
                request.POST.get("email_notifications")
            )

            notification_settings.course_updates = bool(
                request.POST.get("course_updates")
            )

            notification_settings.enroll_updates = bool(
                request.POST.get("enroll_updates")
            )

            notification_settings.save()

            messages.success(request, "Notification preferences updated!")
            return redirect("account_settings")

    return render(request, "student/account_settings.html", {
        "step": step,
        "notification_settings": notification_settings
    })

def confirm_password_change(request, token):

    password_request = get_object_or_404(
        PasswordChangeRequest,
        token=token,
        is_confirmed=False
    )

    if timezone.now() > password_request.created_at + timedelta(minutes=15):
        password_request.delete()
        messages.error(request, "Password confirmation link has expired.")
        return redirect("account_settings")

    user = password_request.user

    user.password = password_request.new_password
    user.save()
    update_session_auth_hash(request, user)

    password_request.is_confirmed = True
    password_request.save()

    return redirect(f"{reverse('account_settings')}?step=success")

@login_required
def profile_view_or_edit(request, mode=None):
    profile, created = Profile.objects.get_or_create(user=request.user)

    is_editing = (mode == 'edit')

    if request.method == 'POST' and is_editing:
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserDisplayForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_view')

    else:
        profile_form = ProfileForm(instance=profile)
        user_form = UserDisplayForm(instance=request.user)

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'user_form': user_form,
        'is_editing': is_editing,
    }
    return render(request, 'student/student_profile.html', context)

@login_required
def student_my_activity(request):
    user = request.user
    enrollments = Enrollment.objects.filter(student=user).select_related("course")
    selected_course_id = request.GET.get("course")
    selected_course = None

    if selected_course_id:
        selected_enrollment = enrollments.filter(course_id=selected_course_id).first()
        if selected_enrollment:
            selected_course = selected_enrollment.course

    filtered_enrollments = enrollments
    if selected_course:
        filtered_enrollments = enrollments.filter(course=selected_course)

    course_progress = []

    for enroll in filtered_enrollments:
        course = enroll.course
        lectures = Lecture.objects.filter(module__course=course)
        total_lectures = lectures.count()

        completed = LectureProgress.objects.filter(
            student=user,
            lecture__in=lectures,
            completed=True
        ).count()

        percent = round((completed / total_lectures) * 100, 2) if total_lectures > 0 else 0

        course_progress.append({
            "course": course,
            "total_lectures": total_lectures,
            "completed_lectures": completed,
            "progress_percent": percent,
        })

    recent_videos = LectureProgress.objects.filter(
        student=user,
        completed=True
    ).select_related("lecture", "lecture__module__course")

    video_lessons_watched = recent_videos

    if selected_course:
        recent_videos = recent_videos.filter(
            lecture__module__course=selected_course
        )
        video_lessons_watched = video_lessons_watched.filter(
            lecture__module__course=selected_course
        )

    recent_videos = recent_videos.order_by("-updated_at")[:10]
    video_lessons_watched = video_lessons_watched.order_by("-updated_at")

    quiz_activity = QuizResult.objects.filter(student=user)

    if selected_course:
        quiz_activity = quiz_activity.filter(quiz__course=selected_course)

    quiz_activity = quiz_activity.select_related(
        "quiz", "quiz__course"
    ).order_by("-submitted_at")

    if selected_course:
        all_live_classes = LiveClass.objects.filter(course=selected_course)
    else:
        enrolled_course_ids = enrollments.values_list("course_id", flat=True)
        all_live_classes = LiveClass.objects.filter(course_id__in=enrolled_course_ids)

    total_classes = all_live_classes.count()

    attendance_records = LiveClassAttendance.objects.filter(
        user=user,
        live_class__in=all_live_classes
    ).select_related("live_class", "live_class__course")

    attended_count = attendance_records.exclude(joined_at=None).count()

    attendance_percent = (
        round((attended_count / total_classes) * 100, 2)
        if total_classes > 0 else 0
    )

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
                "duration": f"{rec.duration} mins" if rec.duration else "—",
            }
            for rec in attendance_records
        ]
    }

    feedback_activity = Feedback.objects.filter(student=user)

    if selected_course:
        feedback_activity = feedback_activity.filter(course=selected_course)

    feedback_activity = feedback_activity.select_related(
        "course", "instructor"
    ).order_by("-created_at")

    qna_activity = LectureQuestion.objects.filter(student=user)

    if selected_course:
        qna_activity = qna_activity.filter(
            lecture__module__course=selected_course
        )

    qna_activity = qna_activity.select_related(
        "lecture", "lecture__module", "lecture__module__course"
    ).prefetch_related("replies__user").order_by("-created_at")

    total_completed = LectureProgress.objects.filter(
        student=user,
        completed=True
    )

    total_lectures = Lecture.objects.all()

    if selected_course:
        total_completed = total_completed.filter(
            lecture__module__course=selected_course
        )
        total_lectures = total_lectures.filter(
            module__course=selected_course
        )

    total_completed_count = total_completed.count()
    total_lectures_count = total_lectures.count()

    overall_progress = (
        round((total_completed_count / total_lectures_count) * 100, 2)
        if total_lectures_count > 0 else 0
    )

    login_history = LoginHistory.objects.filter(user=user).order_by("-login_time")[:25]

    context = {
        "enrollments": enrollments,
        "selected_course": selected_course,
        "total_enrolled_courses": enrollments.count(),
        "total_completed_lectures": total_completed_count,
        "overall_progress": overall_progress,
        "course_progress": course_progress,
        "recent_videos": recent_videos,
        "quiz_activity": quiz_activity,
        "video_lessons_watched": video_lessons_watched,
        "attendance_data": attendance_data,
        "login_history": login_history,
        "qna_activity": qna_activity,
        "feedback_activity": feedback_activity,
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
    if request.method == "POST":
        form = InstructorSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            InstructorProfile.objects.create(
                user=user,
            )

            verification, _ = EmailVerification.objects.get_or_create(user=user)

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

            return render(request, "users/signup_page.html", {
                "student_form": StudentSignUpForm(),
                "instructor_form": form,
            })

    return redirect("signup_page")


def instructor_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            if user.role == "instructor":
                login(request, user)
                return redirect("instructor_dashboard")
            else:
                messages.error(request, "This login is only for instructors.")
    else:
        form = AuthenticationForm()

    form.fields["username"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Enter your email"
    })

    form.fields["password"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Enter your password",
        "id": "id_password"
    })

    return render(request, "instructor/instructor_login.html", {"form": form})


@login_required
def instructor_dashboard(request):

    if request.user.role != "instructor":
        return redirect("auth_page") 

    instructor = request.user

    check_and_send_reminders(instructor)

    courses = Course.objects.filter(instructor=instructor)

    unread_count = Notification.objects.filter(
        user=instructor,
        is_read=False
    ).count()

    total_students = Enrollment.objects.filter(
        course__instructor=instructor
    ).values("student").distinct().count()

    total_earnings = Enrollment.objects.filter(
        course__instructor=instructor
    ).aggregate(
        total=Sum("course__price")
    )["total"] or 0

    return render(
        request,
        "instructor/instructor_dashboard.html",
        {
            "courses": courses,
            "total_students": total_students,
            "unread_count": unread_count,
            "total_earnings": total_earnings,
        },
    )
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("auth_page")

def admin_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("admin_login")

def custom_password_reset(request):
    """
    Step 1: Request password reset
    """
    if request.method == "POST":
        email = request.POST.get("email")

        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_path = reverse(
                "password_reset_confirm",
                kwargs={"uidb64": uid, "token": token}
            )
            reset_url = f"{request.scheme}://{request.get_host()}{reset_path}"

            subject = "Password Reset Request - Speshway"
            message = f"""
Hello {user.first_name or user.username},

You requested a password reset for your Speshway account.

Reset your password using the link below:
{reset_url}

If you didn’t request this, you can safely ignore this email.

Thanks,
Speshway Team
"""

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,  
            )

        return redirect("password_reset_sent")

    return render(request, "forgot_password.html")

def custom_password_reset_confirm(request, uidb64, token):
    """
    Step 2: Set new password
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        messages.error(request, "Invalid or expired reset link.")
        return redirect("auth_page")

    if not default_token_generator.check_token(user, token):
        messages.error(request, "This password reset link has expired.")
        return redirect("auth_page")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not new_password or len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "password_reset_confirm.html")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "password_reset_confirm.html")

        user.set_password(new_password)
        user.save()

        return redirect("password_reset_complete")

    return render(request, "password_reset_confirm.html")

def password_reset_complete(request):
    return render(request, "password_reset_complete.html")


def password_reset_sent(request):
    return render(request, 'password_reset_done.html')


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
        return redirect("auth_page")

    user = request.user
    step = request.GET.get("step", "form")

    notification_settings, created = NotificationSettings.objects.get_or_create(user=user)

    if request.method == 'POST':

        if 'change_password' in request.POST:
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

            PasswordChangeRequest.objects.filter(
                user=user,
                is_confirmed=False
            ).delete()

            change_request = PasswordChangeRequest.objects.create(
                user=user,
                new_password=make_password(new_password1)
            )

            confirm_link = request.build_absolute_uri(
                reverse('inst_confirm_password_change',
                args=[str(change_request.token)])
            )

            send_mail(
                subject="Confirm Your Password Change - Speshway",
                message=f"""
Hello {user.first_name},

Click the link below to confirm your password change:

{confirm_link}

This link will expire in 15 minutes.

If this wasn't you, ignore this email.
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return redirect(f"{reverse('instructor_account_settings')}?step=email_sent")

        elif 'update_notifications' in request.POST:

            notification_settings.email_notifications = bool(
                request.POST.get("email_notifications")
            )

            notification_settings.course_updates = bool(
                request.POST.get("course_updates")
            )

            notification_settings.enroll_updates = bool(
                request.POST.get("enroll_updates")
            )

            notification_settings.save()

            messages.success(request, "Notification preferences updated!")
            return redirect('instructor_account_settings')

    return render(request, 'instructor/instructor_account_settings.html', {
        'user': user,
        'step': step,
        'notification_settings': notification_settings
    })


def inst_confirm_password_change(request, token):

    change_request = get_object_or_404(
        PasswordChangeRequest,
        token=token,
        is_confirmed=False
    )

    if timezone.now() > change_request.created_at + timedelta(minutes=15):
        change_request.delete()
        messages.error(request, "Password confirmation link has expired.")
        return redirect('instructor_account_settings')

    user = change_request.user

    user.password = change_request.new_password
    user.save()
    update_session_auth_hash(request, user)

    change_request.is_confirmed = True
    change_request.save()
    
    return redirect(f"{reverse('instructor_account_settings')}?step=success")

@login_required
def post_login_redirect_view(request):
    user = request.user
    if not hasattr(user, 'role'):
        messages.error(request, "User role not defined.")
        return redirect("auth_page")
    
    if user.role == "student":
        return redirect("student_dashboard")
    elif user.role == "instructor":
        return redirect("instructor_dashboard")
    elif user.role == "admin":
        return redirect("admin_dashboard")
    else:
        return redirect("auth_page")
    

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            if user.role == "admin":
                login(request, user)
                return redirect("admin_dashboard")

            else:
                messages.error(request, "Access denied. Admin login only.")
                return redirect("auth_page")

        else:
            messages.error(request, "Invalid username or password")

    return render(request, "users/admin_login.html")

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
@staff_member_required
def admin_dashboard(request):

    pending_courses = Course.objects.filter(status="pending").order_by('-created_at')

    context = {
        "pending_courses": pending_courses,
        "total_courses": Course.objects.count(),
        "pending_count": pending_courses.count(),
        "total_instructors": User.objects.filter(role="instructor").count(),
        "total_students": User.objects.filter(role="student").count(),
        "notifications": Notification.objects.filter(user=request.user, is_read=False),
    }

    return render(request, "admin/admin_dashboard.html", context)


@staff_member_required
def admin_view_instructor(request, user_id):
    instructor = get_object_or_404(User, id=user_id, role="instructor")

    profile = InstructorProfile.objects.filter(user=instructor).first()
    courses = Course.objects.filter(instructor=instructor)

    total_revenue = Enrollment.objects.filter(
        course__instructor=instructor
    ).aggregate(total=Sum("course__price"))["total"] or 0

    try:

        avg_rating = CourseReview.objects.filter(
            course__instructor=instructor
        ).aggregate(avg=Avg("rating"))["avg"] or 0
    except:
        avg_rating = 0

    context = {
        "user_obj": instructor,
        "profile": profile,
        "courses": courses,
        "total_revenue": total_revenue,
        "avg_rating": round(avg_rating, 1),
    }

    return render(request, "admin/view_instructor.html", context)

@staff_member_required
def admin_view_student(request, user_id):
    student = get_object_or_404(User, id=user_id, role="student")

    profile = Profile.objects.filter(user=student).first()
    enrollments = Enrollment.objects.filter(student=student)

    completed_courses = 0
    total_progress = 0
    course_count = enrollments.count()

    for enrollment in enrollments:
        course = enrollment.course

        total_lectures = Lecture.objects.filter(
            module__course=course
        ).count()

        completed_lectures = LectureProgress.objects.filter(
            student=student,
            lecture__module__course=course,
            completed=True
        ).count()

        if total_lectures > 0:
            progress_percent = (completed_lectures / total_lectures) * 100
            total_progress += progress_percent

            if progress_percent == 100:
                completed_courses += 1

    avg_progress = round(total_progress / course_count, 1) if course_count > 0 else 0

    context = {
        "user_obj": student,
        "profile": profile,
        "enrollments": enrollments,
        "completed_courses": completed_courses,
        "avg_progress": avg_progress,
    }

    return render(request, "admin/view_student.html", context)

@staff_member_required
def toggle_suspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    user.is_suspended = not user.is_suspended
    user.save()

    return redirect(request.META.get("HTTP_REFERER"))