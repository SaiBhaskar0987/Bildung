from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
 
from .forms import StudentSignUpForm, InstructorSignUpForm
from courses.models import Course
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
 
 
 
# --- Auth Landing Page (just options, no forms) ---
def auth_page(request):
    return render(request, "users/auth_page.html")
 
 
# --- Student Signup ---
def student_signup(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "student"
            user.save()
            login(request, user)
            return redirect("student_dashboard")
    else:
        form = StudentSignUpForm()
    return render(request, "users/student_signup.html", {"form": form})
 
 
# --- Instructor Signup ---
# --- Instructor Signup ---
def instructor_signup(request):
    if request.method == "POST":
        form = InstructorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "instructor"
 
            # ✅ Hash the password before saving
            raw_password = form.cleaned_data.get("password1") or form.cleaned_data.get("password")
            if raw_password:
                user.set_password(raw_password)
 
            user.save()
            login(request, user)
            return redirect("instructor:instructor_dashboard")
    else:
        form = InstructorSignUpForm()
    return render(request, "users/instructor_signup.html", {"form": form})
 
 
# --- Student Login ---
def student_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == "student":
                login(request, user)
                return redirect("student_dashboard")
            else:
                messages.error(request, "This login is only for students.")
    else:
        form = AuthenticationForm()
    return render(request, "users/student_login.html", {"form": form})
 
 
# --- Instructor Login ---
def instructor_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == "instructor":
                login(request, user)
                return redirect("instructor:instructor_dashboard")
            else:
                messages.error(request, "This login is only for instructors.")
    else:
        form = AuthenticationForm()
    return render(request, "users/instructor_login.html", {"form": form})
 
 
# --- Logout (works for all roles) ---
def logout_view(request):
    logout(request)
    return redirect("auth_page")
 
 
# --- Dashboards ---
@login_required(login_url="/auth/")
def student_dashboard(request):
    if request.user.role != "student":
        return redirect("auth_page")
    enrolled_courses = Course.objects.filter(enrollments__student=request.user)
    return render(request, "courses/student_dashboard.html", {"enrolled_courses": enrolled_courses})
 
 
@login_required(login_url="/auth/")
def instructor_dashboard(request):
    if request.user.role != "instructor":
        return redirect("auth_page")
    courses = Course.objects.filter(instructor=request.user)
    return render(request, "courses/instructor_dashboard.html", {"courses": courses})
 
 
@login_required(login_url="/auth/")
def admin_dashboard(request):
    if request.user.role != "admin":
        return redirect("auth_page")
    return render(request, "admin/dashboard.html")
 
 
@login_required
def post_login_redirect(request):
    user = request.user
    role = getattr(user, 'role', None)
    if role == 'instructor':
        return redirect('courses:instructor_home')
    if role == 'student':
        return redirect('students:dashboard')   # adjust if your student dashboard URL name is different
    return redirect('home')  # fallback

def signup_view(request):
    """
    Handles user registration and sends a welcome email.
    The email content will be printed to the terminal because of the
    'console.EmailBackend' setting in settings.py.
    """
    if request.method == 'POST':
        # --- 1. SIMULATE FORM PROCESSING AND USER CREATION ---
        # In a real app, you would validate the form data here.
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Dummy checks for demonstration
        if not username or not email:
            return render(request, 'signup.html', {'error': 'Please fill in both fields.'})

        try:
            # Simulate user creation (replace with actual User.objects.create_user)
            # user = User.objects.create_user(username, email, 'password123')
            
            # --- 2. THE EMAIL SENDING COMMAND ---
            # This is the line that triggers the email output in your console.
            send_mail(
                # Subject
                'Welcome to Our Awesome Site, ' + username + '!',
                
                # Message (Body of the email)
                f'Thank you for signing up for our service. We are excited to have you!\n\nYour username is: {username}',
                
                # From email (uses DEFAULT_FROM_EMAIL from settings.py)
                settings.DEFAULT_FROM_EMAIL,
                
                # Recipient list
                [email],
                
                # Fail silently? (Always keep this False in development to see errors)
                fail_silently=False,
            )
            
            # Print a confirmation message to the actual terminal
            print(f"\n[CONSOLE EMAIL BACKEND] Successfully generated and printed welcome email for: {email}")

            return redirect('/success') # Redirect to a success page
        
        except Exception as e:
            # In a real app, you'd handle specific form/database errors
            print(f"An error occurred during signup: {e}")
            return render(request, 'signup.html', {'error': 'Signup failed due to an internal error.'})

    return render(request, 'users/signup.html')


# Placeholder for a success view (optional)
def success_view(request):
    return render(request, 'success.html')