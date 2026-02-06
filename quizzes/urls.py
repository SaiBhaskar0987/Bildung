from django.urls import path
from . import views

urlpatterns = [
    path("<int:course_id>/", views.quiz_list, name="quiz_list"),
    path("take/<int:quiz_id>/", views.take_quiz, name="take_quiz"),
    
    path("result/<int:quiz_id>/", views.quiz_result, name="quiz_result"),
    path("course/<int:course_id>/quiz/<int:quiz_id>/preview/", views.preview_quiz, name="quiz_preview"),
]
