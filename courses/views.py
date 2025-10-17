from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime


from .models import Course, Enrollment, Lecture, LectureProgress, Feedback, CourseEvent
from .forms import CourseForm, LectureForm, FeedbackForm
from users.decorators import instructor_required

# -------------------------------
# Common Views
# -------------------------------

def course_list(request):
    """Public list of all available courses"""
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required(login_url='/login/')
def browse_courses(request):
    """Student: browse unenrolled courses"""
    if getattr(request.user, 'role', None) != 'student':
        return redirect('login')

    available_courses = Course.objects.exclude(students=request.user)
    return render(request, 'courses/browse_courses.html', {'courses': available_courses})


# -------------------------------
# Student Views
# -------------------------------

@login_required(login_url='/login/')
def enroll_course(request, course_id):
    """Student: enroll in a course"""
    if getattr(request.user, 'role', None) != 'student':
        return redirect('login')

    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    messages.success(request, f"Enrolled in {course.title}")
    return redirect('student_dashboard')


@login_required(login_url='/login/')
def student_course_detail(request, course_id):
    """Student: view course details + progress"""
    course = get_object_or_404(Course, id=course_id, students=request.user)
    lectures = course.lectures.all()

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
    """Student: mark lecture complete"""
    lecture = get_object_or_404(Lecture, id=lecture_id)
    course = lecture.course

    if getattr(request.user, 'role', None) != 'student':
        return redirect('login')

    LectureProgress.objects.get_or_create(
        student=request.user,
        lecture=lecture,
        defaults={'completed': True}
    )
    return redirect('student_course_detail', course_id=course.id)


# -------------------------------
# Instructor Views
# -------------------------------

@login_required
def instructor_dashboard(request):
    """Instructor dashboard"""
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/instructor/home.html', {'courses': courses})



@login_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, "Course created successfully.")
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()
    return render(request, 'courses/instructor/add_course.html', {'form': form})


@login_required
def course_edit(request, course_id):
    """Instructor: edit existing course"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect('instructor_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/instructor/course_edit.html', {'form': form, 'course': course})



@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lectures = course.lectures.all().order_by('created_at')
    return render(request, 'courses/instructor/course_detail.html', {'course': course, 'lectures': lectures})



@login_required
def add_lecture(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = LectureForm(request.POST, request.FILES)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.course = course
            lecture.save()
            messages.success(request, "Lecture added successfully.")
            return redirect('instructor:course_detail', course_id=course.id)
    else:
        form = LectureForm()
    return render(request, 'courses/instructor/add_lecture.html', {'form': form, 'course': course})



@login_required
def edit_lecture(request, course_id, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id, course__id=course_id, course__instructor=request.user)
    if request.method == "POST":
        form = LectureForm(request.POST, request.FILES, instance=lecture)
        if form.is_valid():
            form.save()
            messages.success(request, "Lecture updated successfully.")
            return redirect('instructor:course_detail', course_id=course_id)
    else:
        form = LectureForm(instance=lecture)
    return render(request, 'courses/instructor/edit_lecture.html', {'form': form, 'course_id': course_id})


@login_required
def delete_lecture(request, course_id, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id, course__id=course_id, course__instructor=request.user)
    if request.method == "POST":
        lecture.delete()
        messages.success(request, "Lecture deleted successfully.")
        return redirect('instructor:course_detail', course_id=course_id)
    return render(request, 'courses/instructor/delete_lecture.html', {'lecture': lecture, 'course_id': course_id})


@login_required
def course_progress_report(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    enrollments = Enrollment.objects.filter(course=course)
    progress_data = []
    total_lectures = course.lectures.count()

    for enrollment in enrollments:
        student = enrollment.student
        completed = LectureProgress.objects.filter(student=student, lecture__course=course, completed=True).count()
        progress = (completed / total_lectures * 100) if total_lectures else 0
        progress_data.append({"student": student, "completed": completed, "total": total_lectures, "progress": progress})

    return render(request, 'courses/instructor/course_progress_report.html', {'course': course, 'progress_data': progress_data})


@login_required
def add_event(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = parse_datetime(request.POST.get('start_time'))
        end_time = parse_datetime(request.POST.get('end_time'))

        CourseEvent.objects.create(course=course, title=title, description=description, start_time=start_time, end_time=end_time)
        messages.success(request, "Event added successfully.")
        return redirect('instructor:course_detail', course_id=course.id)

    return render(request, 'courses/instructor/add_event.html', {'course': course})



@login_required
def give_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.instructor = request.user
            feedback.course = course
            feedback.save()
            messages.success(request, "Feedback submitted successfully!")
            return redirect('instructor:course_detail', course_id=course.id)
    else:
        form = FeedbackForm()
       
    return render(request, 'courses/instructor/give_feedback.html', {'form': form, 'course': course})
