from django.urls import path, include
from . import views

urlpatterns = [
    # =====================
    # LANDING / AUTH
    # =====================
    path("auth/", views.auth_page, name="auth_page"),
    path("signup/", views.signup_page, name="signup_page"),

    path('admin-login/', views.admin_login, name='admin_login'),
    path("logout/", views.logout_view, name="logout_view"),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("admin-instructor/<int:user_id>/", views.admin_view_instructor, name="admin_view_instructor"),
    path("admin-student/<int:user_id>/", views.admin_view_student, name="admin_view_student"),
    path("admin-user/<int:user_id>/toggle-suspend/", views.toggle_suspend_user, name="toggle_suspend_user"),

    #verification
    path("check-email/", views.check_email, name="check_email"),
    path("verify/<str:role>/<uuid:token>/", views.verify_email, name="verify_email"),

    # Student
    path("student/signup/", views.student_signup, name="student_signup"),
    path("student/login/", views.student_login, name="student_login"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),


    # ACCOUNT SETTINGS (PASSWORD CONFIRM FLOW)
    path("account-settings/", views.account_settings, name="account_settings"),
    path(
        "password-change-confirm/<uuid:token>/",
        views.confirm_password_change,
        name="confirm_password_change",
    ),

    # =====================
    # STUDENT PAGES
    # =====================
    path("profile/", views.profile_view_or_edit, name="profile_view"),
    path(
        "profile/edit/",
        views.profile_view_or_edit,
        {"mode": "edit"},
        name="profile_edit",
    ),
    path("my-activity/", views.student_my_activity, name="student_my_activity"),

    # Student notifications
    path("students/notifications/", views.student_notifications, name="student_notifications"),
    path(
        "notifications/recent/",
        views.get_recent_notifications,
        name="recent_notifications",
    ),
    path(
        "notifications/mark-read/",
        views.mark_all_notifications,
        name="mark_all_notifications",
    ),
    path(
        "notifications/mark/<int:notif_id>/",
        views.mark_notification,
        name="mark_notification",
    ),

    # =====================
    # CUSTOM PASSWORD RESET
    # =====================
    path("forgot-password/", views.custom_password_reset, name="forgot_password"),
    path("password-reset-sent/", views.password_reset_sent, name="password_reset_sent"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.custom_password_reset_confirm,
        name="password_reset_confirm"
    ),
    path(
        "password-reset-complete/",
        views.password_reset_complete,
        name="password_reset_complete"
    ),

    # =====================
    # STUDENT COURSES
    # =====================
    path(
        "student/",
        include(
            ("courses.student_urls", "student_courses"),
            namespace="student_courses",
        ),
    ),

    # =====================
    # INSTRUCTOR AUTH & DASHBOARD
    # =====================
    path("instructor/signup/", views.instructor_signup, name="instructor_signup"),
    path("instructor/login/", views.instructor_login, name="instructor_login"),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path("instructor/profile/", views.instructor_profile_view_or_edit, name="instructor_profile_view"),
    path("instructor/profile/<str:mode>/", views.instructor_profile_view_or_edit, name="instructor_profile_edit"),
     path("recent-notifications/", views.instructor_recent_notifications, name="instructor_recent_notifications"),
    path("instructor/notifications/", views.instructor_notifications_page, name="instructor_notifications"),
    path("mark-read/<int:notif_id>/", views.instructor_mark_read, name="mark_notification_read"),
    path("mark-all-read/", views.instructor_mark_all_read, name="mark_notifications_read"),
    path("settings/", views.instructor_account_settings, name="instructor_account_settings"),
    path('confirm-password-change/<uuid:token>/', views.inst_confirm_password_change,name='inst_confirm_password_change'),

    # Include all instructor dashboard & course URLs
    path("instructor/", include(("courses.instructor_urls", "instructor"), namespace="instructor")),


    # =====================
    # LOGOUT / REDIRECT
    # =====================
    path("logout/", views.logout_view, name="logout_view"),
    path(
        "post-login/",
        views.post_login_redirect_view,
        name="post_login_redirect",
    ),

    # Post-login redirect
    path("post-login/", views.post_login_redirect_view, name="post_login_redirect"),

    # Google OAuth Routes
    path("google/login/", views.google_oauth_entry, name="google_oauth_entry"),
    path("google-redirect/", views.google_login_redirect, name="google_login_redirect"),
]



    

