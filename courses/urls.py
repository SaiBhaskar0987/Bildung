from django.urls import path
from . import views
from users import views as user_views

app_name = "courses"

urlpatterns = [
    # Public
    #path('', views.course_list, name='course_list'),
    path("course/<int:course_id>/", views.view_course,name="view_course"),


    # Student URLs
    path('student/courses/', views.browse_courses, name='browse_courses'),
    path('student/enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('student/course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('lecture/<int:lecture_id>/complete/', views.mark_lecture_complete, name='mark_lecture_complete'),

    # ✅ Assignment APIs
    path("assignment/create/", views.create_assignment, name="create_assignment"),
    path("assignment/<int:assignment_id>/save/", views.save_assignment, name="save_assignment"),
    path("assignment/<int:assignment_id>/questions/save/",views.save_assignment_questions,name="save_assignment_questions"),
    path("assignment/<int:assignment_id>/start/",views.start_assignment,name="start_assignment"),
    path("assignment/<int:assignment_id>/take/",views.take_assignment,name="take_assignment"),
    path("assignment/<int:assignment_id>/submit/",views.submit_assignment,name="submit_assignment"),
    path("assignment/<int:assignment_id>/result/",views.assignment_result,name="assignment_result"),
    # ✅ AI API
    path("rag/generate-answer", views.rag_generate_answer, name="rag_generate_answer"),

    # Public (KEEP LAST)
    path("", views.course_list, name="course_list"),
    # admin
    path('admin/approve/<int:course_id>/', views.admin_approve_course, name='admin_approve_course'),
    path('admin/reject/<int:course_id>/', views.admin_reject_course, name='admin_reject_course'),
    path('admin/notifications/', views.admin_notifications, name='admin_notifications'),
    path('admin/notifications/read/<int:notif_id>/', views.mark_admin_notification_read, name='mark_admin_notification_read'),
    path('admin/notifications/read-all/', views.mark_all_admin_notifications_read, name='mark_all_admin_notifications_read'),
    path("admin/course/<int:course_id>/", views.admin_course_detail, name="admin_course_detail"),
    path('admin/courses/', views.admin_courses, name='admin_courses'),
    path("admin/course/<int:course_id>/", views.admin_course_detail, name="admin_course_detail"),

    path("admin/instructors/", views.admin_instructors, name="admin_instructors"),

    path("admin/students/", views.admin_students, name="admin_students"),
 
    path("admin/user/<int:user_id>/delete/", views.delete_user_admin, name="delete_user_admin"),

    path("admin/course/<int:course_id>/delete/", views.admin_delete_course, name="admin_delete_course"),
    path("admin/quiz/<int:quiz_id>/preview/", views.admin_quiz_preview, name="admin_quiz_preview"),
    path("admin/instructor/<int:instructor_id>/courses/", views.admin_instructor_courses, name="admin_instructor_courses"),
    path("admin/student/<int:student_id>/courses/", views.admin_student_courses,name="admin_student_courses"),
    path("admin/remove-enrollment/<int:enrollment_id>/", views.admin_remove_enrollment, name="admin_remove_enrollment"),

    path('admin/comment/<int:course_id>/<str:target>/', views.admin_add_comment, name='admin_add_comment'),

    path('admin/comment/<int:course_id>/<str:target>/<int:object_id>/', views.admin_add_comment, name='admin_add_comment'),

]
