from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, LectureProgress, Lecture, Feedback, CourseEvent
from django.contrib import messages
from .forms import CourseForm, LectureForm, FeedbackForm
from django.utils import timezone


def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required(login_url='/login/')
def create_course(request):
    if request.user.role != 'instructor':
        return redirect('login')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})



@login_required
def enroll_course(request, course_id):
    if request.user.role != "student":
        messages.error(request, "Only students can enroll.")
        return redirect("course_list")

    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    messages.success(request, f"Enrolled in {course.title}.")
    return redirect("course_list")


@login_required
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'instructor/dashboard.html', {'courses': courses})

@login_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()
    return render(request, 'instructor/add_course.html', {'form': form})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lectures = course.lectures.all().order_by('order')
    return render(request, 'instructor/course_detail.html', {'course': course, 'lectures': lectures})

@login_required(login_url='/login/')
def add_lecture(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == "POST":
        form = LectureForm(request.POST, request.FILES)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.course = course
            lecture.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = LectureForm()
    return render(request, 'courses/add_lecture.html', {'form': form, 'course': course})

@login_required
def give_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == "POST":
        form = FeedbackForm(request.POST, course=course)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.course = course
            feedback.instructor = request.user
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect('course_detail', course_id=course.id)
    else:
        form = FeedbackForm(course=course)

    return render(request, 'courses/give_feedback.html', {
        'course': course,
        'form': form,
    })



@login_required(login_url='/login/')
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # If instructor -> show instructor detail template
    if request.user.role == 'instructor' and course.instructor == request.user:
        return render(request, 'courses/instructor_course_detail.html', {'course': course})

    # If student -> check enrollment
    if request.user.role == 'student':
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        if is_enrolled:
            return render(request, 'courses/student_course_detail.html', {'course': course})
        else:
            # Not enrolled → deny access
            return render(request, 'courses/access_denied.html', {'course': course})

    # If neither instructor nor student
    return redirect('login')


@login_required(login_url='/login/')
def enroll_in_course(request, course_id):
    if request.user.role != 'student':
        return redirect('login')

    course = get_object_or_404(Course, id=course_id)
    course.students.add(request.user)  # add student to course
    return redirect('student_dashboard')



@login_required(login_url='/login/')
def mark_lecture_complete(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    course = lecture.course

    # Ensure student is enrolled
    enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if request.user.role != 'student' or not enrolled:
        return redirect('access_denied', course_id=course.id)

    # Update or create progress record
    progress, created = LectureProgress.objects.get_or_create(student=request.user, lecture=lecture)
    progress.completed = True
    progress.save()

    return redirect('course_detail', course_id=course.id)


@login_required(login_url='/login/')
def course_progress_report(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    enrollments = Enrollment.objects.filter(course=course)
    progress_data = []

    for enrollment in enrollments:
        student = enrollment.student
        completed = LectureProgress.objects.filter(student=student, lecture__course=course, completed=True).count()
        total = course.lectures.count()
        progress_percent = (completed / total * 100) if total > 0 else 0
        progress_data.append({"student": student, "completed": completed, "total": total, "progress": progress_percent})

    return render(request, 'courses/course_progress_report.html', {'course': course, 'progress_data': progress_data})



@login_required(login_url='/login/')
def add_event(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        CourseEvent.objects.create(
            course=course,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time
        )
        return redirect('course_detail', course_id=course.id)

    return render(request, 'courses/add_event.html', {'course': course})


@login_required(login_url='/login/')
def student_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, students=request.user)
    lectures = course.lectures.all()

    # Progress tracking
    total = lectures.count()
    completed = LectureProgress.objects.filter(
        student=request.user, lecture__in=lectures, completed=True
    ).count()

    progress_map = {
        lp.lecture_id: lp.completed
        for lp in LectureProgress.objects.filter(student=request.user, lecture__in=lectures)
    }

    return render(request, 'courses/student_course_detail.html', {
        'course': course,
        'lectures': lectures,
        'total': total,
        'completed': completed,
        'progress_map': progress_map
    })


@login_required(login_url='/login/')
def mark_lecture_complete(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    LectureProgress.objects.get_or_create(
        student=request.user,
        lecture=lecture,
        defaults={'completed': True}
    )
    return redirect('student_course_detail', course_id=lecture.course.id)


@login_required(login_url='/login/')
def browse_courses(request):
    if request.user.role != 'student':
        return redirect('login')

    # show all courses not yet enrolled by the student
    available_courses = Course.objects.exclude(students=request.user)

    return render(request, 'courses/browse_courses.html', {
        'courses': available_courses
    })
