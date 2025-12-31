🎓 Bildung – Learning Management System

Bildung is a Django-based Learning Management System (LMS) designed to manage online courses with role-based access for Admins, Instructors, and Students.

🚀 Key Features

User authentication & role management

Course creation and enrollment

Instructor & student dashboards

Progress tracking

Secure and scalable architecture

🛠️ Tech Stack

Backend: Python, Django

Frontend: HTML, CSS, JavaScript

Database: MySQL

Version Control:GitHub

⚙️ Setup Instructions

Clone the repository

git clone https://github.com/SaiBhaskar0987/Bildung.git


cd Bildung

Create virtual environment

python -m venv venv

venv\Scripts\activate   

Install dependencies

pip install -r requirements.txt

Apply migrations

python manage.py makemigrations
python manage.py migrate

Run the server

python manage.py runserver


Access the app at:
👉 http://127.0.0.1:8000/

👥 User Roles

Admin: System and user management

Instructor: Create and manage courses

Student: Enroll and learn courses

📌 Future Scope

Payment gateway integration

Certificates for course completion

REST API support

📂 Project Structure

BILDUNG/
│── .myenv1/              # Python virtual environment
│── chat/                 # Real-time chat / messaging features
│── core/                 # Core project settings and configuration
│── courses/              # Course management and learning content
│── forums/               # Discussion forums and interactions
│── home/                 # Home pages and landing views
│── media/                # Uploaded media files
│── quizzes/              # Quizzes, assessments, and evaluations
│── users/                # User authentication and role management
│── manage.py             # Django management script
│── pyproject.toml        # Project metadata and build configuration
│── requirements.txt     # Python dependencies
│── urls.py               # Project-level URL routing
│── README.md             # Project documentation
│── uv_setup.md           # Environment / UV setup notes

🧩 Django Apps Overview

core:
Contains global Django configuration including settings, middleware, and core utilities.

users:
Handles user authentication, authorization, profiles, and role-based access (Admin, Instructor, Student).

courses:
Manages course creation, modules, lectures, enrollment, and student progress tracking.

quizzes:
Implements quizzes, questions, answers, scoring, and evaluations.

forums:
Enables discussion boards for student and instructor communication.

chat:
Provides real-time or internal messaging functionality.

home:
Manages landing pages, dashboards, and general navigation views.