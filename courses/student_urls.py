from django.urls import path
from . import views
app_name = 'student'  # <- THIS IS REQUIRED
urlpatterns = [
    path('courses/', views.browse_courses, name='browse_courses'),
    path('courses/', views.student_course_list, name='student_course_list'),
    path('courses/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('lectures/<int:lecture_id>/complete/', views.mark_lecture_complete, name='mark_lecture_complete'),
    path('courses/<int:course_id>/progress/', views.student_progress, name='student_progress'),
    path("my-courses/", views.my_courses, name="my_courses"),
    path('get-certificate/<int:course_id>/', views.get_certificate, name='get_certificate'),
    path('my-certificates/', views.my_certificates, name='my_certificates'),
    path('lectures/<int:lecture_id>/undo/', views.undo_lecture_completion, name='undo_lecture_completion'),
    path('lecture/<int:lecture_id>/auto_complete/', views.auto_mark_complete, name='auto_mark_complete'),
    path('upcoming-classes/', views.student_upcoming_classes, name='student_upcoming_classes'),
    path('account-settings/', views.account_settings, name='account_settings'),
    path('my-activity/', views.my_activity, name='my_activity'),

    path('lecture/<int:lecture_id>/ask/', views.ask_question, name='ask_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('course/<int:course_id>/qna/', views.course_qna, name='course_qna'),
    path("reply/<int:reply_id>/upvote/", views.upvote_reply, name="upvote_reply"),
    path("course/<int:course_id>/leave-review/", views.leave_review, name="leave_review"),

]