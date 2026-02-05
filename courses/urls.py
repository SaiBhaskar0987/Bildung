from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
   
   
    # Student URLs
    path("student/courses/", views.browse_courses, name="browse_courses"),
    path("student/enroll/<int:course_id>/", views.enroll_course, name="enroll_course"),
    path("student/course/<int:course_id>/", views.student_course_detail, name="student_course_detail"),
    path("lecture/<int:lecture_id>/complete/", views.mark_lecture_complete, name="mark_lecture_complete"),

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

]
