from django import forms
from django.utils.text import slugify
from .models import Course, Lecture, Feedback, Enrollment, Module
from django.forms import inlineformset_factory


# --------------------------
# Course Form (with category)
# --------------------------
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'category']  # Added 'category'
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}


# --------------------------
# Module Form
# --------------------------
class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']


# --------------------------
# Lecture Form
# --------------------------
class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'video', 'file']


# --------------------------
# Inline Formsets
# --------------------------
# Added fk_name='course' to fix: "'Module' has no ForeignKey to 'Course'"
ModuleFormSet = inlineformset_factory(
    parent_model=Course,
    model=Module,
    form=ModuleForm,
    fk_name='course',
    extra=1,
    can_delete=True
)

LectureFormSet = inlineformset_factory(
    parent_model=Module,
    model=Lecture,
    form=LectureForm,
    extra=1,
    can_delete=True
)


# --------------------------
# Feedback Form
# --------------------------
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write feedback here...'}),
        }

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)  # passed from view
        super().__init__(*args, **kwargs)
        if course:
            # restrict feedback to enrolled students
            enrolled_students = Enrollment.objects.filter(course=course).values_list("student", flat=True)
            self.fields['student'].queryset = course.students.filter(id__in=enrolled_students)
