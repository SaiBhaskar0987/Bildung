from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizChoice, QuizQuestion, StudentAnswer,  QuizResult
from courses.models import Course, LectureProgress, Module
import random
from django.contrib import messages


@login_required
def quiz_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = course.quizzes.all()
    return render(request, "quizzes/quiz_list.html", {"course": course, "quizzes": quizzes})


PASS_PERCENT = 45
MAX_ATTEMPTS = 3

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    result, created = QuizResult.objects.get_or_create(
        quiz=quiz,
        student=request.user,
        defaults={"attempts": 0}
    )

    if result.passed:
        messages.info(request, "You already passed this quiz.")
        return redirect("student:student_course_detail", course_id=quiz.course.id)

    if result.attempts >= MAX_ATTEMPTS:
        messages.error(request, "Maximum attempts reached.")
        return redirect("student:student_course_detail", course_id=quiz.course.id)

    questions = list(quiz.questions.prefetch_related("choices"))

    random.shuffle(questions)

    for q in questions:
        q.shuffled_choices = list(q.choices.all())
        random.shuffle(q.shuffled_choices)

    if request.method == "POST":
        score = 0

        for question in questions:
            selected_choice_id = request.POST.get(f"q_{question.id}")
            if not selected_choice_id:
                continue

            choice = QuizChoice.objects.filter(
                id=selected_choice_id,
                question=question
            ).first()

            if not choice:
                continue

            StudentAnswer.objects.update_or_create(
                student=request.user,
                question=question,
                defaults={"choice": choice},
            )

            if choice.is_correct:
                score += 1

        total = len(questions)
        percent = (score / total) * 100 if total else 0

        result.attempts += 1
        result.score = score
        result.completed = True
        result.passed = percent >= PASS_PERCENT
        result.save()

        if result.passed:
            messages.success(request, f"Quiz passed! Score: {percent:.0f}%")
        else:
            remaining = MAX_ATTEMPTS - result.attempts

            if remaining > 0:
                messages.warning(
                    request,
                    f"You scored {percent:.0f}%. Attempts left: {remaining}"
                )
            else:
                messages.error(
                    request,
                    "You failed 3 times. Course restarted from Module 1."
                )

        return redirect("quiz_result", quiz_id=quiz.id)

    return render(
        request,
        "quizzes/take_quiz.html",
        {
            "quiz": quiz,
            "questions": questions,
            "attempts_left": MAX_ATTEMPTS - result.attempts
        }
    )


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    result = QuizResult.objects.filter(
        quiz=quiz,
        student=request.user
    ).first()

    if not result:
        messages.error(request, "You have not attempted this quiz.")
        return redirect(
            "student:student_course_detail",
            course_id=quiz.course.id
        )

    if result.attempts >= 3 and not result.passed:
        messages.error(request, "Course restarted due to failed attempts.")
        return redirect(
            "student:student_course_detail",
            course_id=quiz.course.id
        )

    answers = (
        StudentAnswer.objects
        .filter(student=request.user, question__quiz=quiz)
        .select_related("question", "choice")
        .prefetch_related("question__choices")
    )

    total_questions = quiz.questions.count()

    percent = round(
        (result.score / total_questions) * 100,
        2
    ) if total_questions else 0

    passed = percent >= PASS_PERCENT

    if passed:
        for a in answers:
            a.correct_choice = next(
                (c for c in a.question.choices.all() if c.is_correct),
                None
            )

    return render(
        request,
        "quizzes/quiz_result.html",
        {
            "quiz": quiz,
            "course_id": quiz.course.id,
            "result": result,
            "answers": answers,
            "percent": percent,
            "passed": passed,
            "attempts": result.attempts,
            "pass_percent": PASS_PERCENT,
            "total_questions": total_questions,
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