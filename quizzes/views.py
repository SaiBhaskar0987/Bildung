from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizChoice, QuizQuestion, StudentAnswer,  QuizResult
from courses.models import Course

@login_required
def quiz_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = course.quizzes.all()
    return render(request, "quizzes/quiz_list.html", {"course": course, "quizzes": quizzes})


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related("choices")

    if request.method == "POST":
        score = 0

        for question in questions:
            selected_choice_id = request.POST.get(f"q_{question.id}")
            if not selected_choice_id:
                continue

            choice = get_object_or_404(QuizChoice, id=selected_choice_id)

            StudentAnswer.objects.update_or_create(
                student=request.user,
                question=question,
                defaults={"choice": choice},
            )

            if choice.is_correct:
                score += 1

        QuizResult.objects.update_or_create(
            quiz=quiz,
            student=request.user,
            defaults={
                "score": score,
                "completed": True,   
            }
        )

        return redirect(
            "student:student_course_detail",
            course_id=quiz.course.id
        )

    return render(
        request,
        "quizzes/take_quiz.html",
        {
            "quiz": quiz,
            "questions": questions,
        }
    )


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    course_id = quiz.course_id

    result = get_object_or_404(
        QuizResult,
        quiz=quiz,
        student=request.user
    )

    answers = (
        StudentAnswer.objects
        .filter(
            student=request.user,
            question__quiz=quiz
        )
        .select_related("question", "choice")
    )

    return render(
        request,
        "quizzes/quiz_result.html",
        {
            "quiz": quiz,
            "course_id": course_id,  
            "result": result,
            "answers": answers
        }
    )


@login_required
def preview_quiz(request, course_id, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        course_id=course_id,
        course__instructor=request.user
    )

    questions = (
        quiz.questions
        .prefetch_related("choices")
        .order_by("created_at")
    )

    if request.method == "POST":
        for q in questions:
            q_text = request.POST.get(f"question_{q.id}")
            if q_text:
                q.question_text = q_text
                q.save()

            correct_choice_id = request.POST.get(f"correct_{q.id}")

            for choice in q.choices.all():
                c_text = request.POST.get(f"choice_{choice.id}")
                if c_text:
                    choice.text = c_text

                choice.is_correct = (
                    str(choice.id) == str(correct_choice_id)
                )

                choice.save()

        return redirect(
            "instructor:quiz_preview",
            course_id=course_id,
            quiz_id=quiz_id
        )

    return render(
        request,
        "quizzes/quiz_preview.html",
        {
            "quiz": quiz,
            "questions": questions
        }
    )