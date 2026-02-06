from django.db import models
from users.models import User
from courses.models import Course


class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    quiz_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["quiz_order", "id"]

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        related_name="questions",
        on_delete=models.CASCADE
    )
    question_text = models.TextField()
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.CharField(
        max_length=1,
        choices=[("A","A"),("B","B"),("C","C"),("D","D")]
    )
    is_auto_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class QuizChoice(models.Model):
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name="choices"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class StudentAnswer(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "student"}
    )
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE
    )
    choice = models.ForeignKey(
        QuizChoice,
        on_delete=models.CASCADE
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} → {self.question.text}"

    
class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"role": "student"})
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("quiz", "student")
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score})"

