from django.urls import path
from courses import views

app_name = 'instructor'

urlpatterns = [

    # Instructor-only course management
    path('courses/add/', views.add_course, name='add_course'),
    path("account-settings/", views.instructor_account_settings, name="account_settings"),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),

    # ✅ ADD THIS LINE 👇
    path(
        "courses/<int:course_id>/assignment/<int:assignment_id>/edit/",
        views.edit_assignment,
        name="edit_assignment"
    ),

    path('courses/<int:course_id>/add-lecture/', views.add_lecture, name='add_lecture'),
    path('courses/<int:course_id>/feedback/', views.give_feedback, name='give_feedback'),
    path('students-list/', views.my_students, name='students_list'),
    path('student/<int:student_id>/', views.view_student_profile, name='view_student_profile'),
    path('courses/<int:course_id>/progress/', views.course_progress_report, name='course_progress_report'),
    path("add-event/", views.add_event, name="add_event"),
    path("schedule_live_class/", views.schedule_live_class, name="schedule_live_class"),
    path("edit-class/<int:class_id>/", views.edit_live_class, name="edit_live_class"),
    path("delete-class/<int:class_id>/", views.delete_live_class, name="delete_live_class"),
    path("edit-event/<int:event_id>/", views.edit_event, name="edit_event"),
    path("delete-event/<int:event_id>/", views.delete_event, name="delete_event"),

    path("calendar/", views.calendar_view, name="calendar_view"),

    path("question/<int:question_id>/reply/", views.add_reply, name="add_reply"),
    path("reply/<int:reply_id>/edit/", views.edit_reply, name="edit_reply"),
    path("reply/<int:reply_id>/delete/", views.delete_reply, name="delete_reply"),
    path("course/<int:course_id>/overview/", views.course_overview, name="course_overview"),
    path("course/<int:course_id>/student/<int:student_id>/history/",
         views.student_history, name="student_history"),

    path("courses/<int:course_id>/edit/", views.edit_course, name="edit_course"),
    path("save/", views.save_course, name="save_course"),
    path("publish/<int:course_id>/", views.publish_course, name="publish_course"),

    path("courses/<int:course_id>/module/<int:module_id>/edit/",
         views.edit_module, name="edit_module"),

    path("courses/<int:course_id>/module/<int:module_id>/module_add/",
         views.add_module, name="add_module"),

    path("module/create/", views.create_module, name="create_module"),
    path("module/<int:module_id>/save/", views.save_module, name="save_module"),
    path("lecture/<int:lecture_id>/delete/", views.delete_lecture, name="delete_lecture"),
    path("module/<int:module_id>/delete/", views.delete_module, name="delete_module"),
]
