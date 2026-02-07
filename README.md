📚 Bildung – AI-Powered E-Learning Platform

Bildung is a full-stack e-learning platform that combines Django for core application logic and FastAPI for AI-powered features such as quiz generation, an AI learning chatbot using RAG (Retrieval-Augmented Generation).

The platform supports instructors and students, structured courses, modules, quizzes, assessments, video/PDF content, dashboards, and personalized recommendations and conversational AI assistance.


🚀 Features:


👨‍🏫 Instructor


Instructor signup with email or Google login

Email verification for instructors

Course creation & editing

Course builder:

Modules

Quizzes

Assessments

Live Classes

Upload video \& PDF lectures

Publish courses

Instructor dashboard


👨‍🎓 Student


Student signup with email or Google login

Email verification for students

Student dashboard

Course enrollment

Course progress tracking

Personalized course recommendations

AI-generated and manual quizzes

Assessments with AI evaluation

AI chatbot for doubt clarification and learning assistance

Course completion certificates


🔐 Authentication & Google OAuth (Google Login)


Bildung supports secure authentication using:

Email & password login

Email verification (for instructors and students)

Google OAuth 2.0 login using social_django

This allows users to sign up or log in using their Google account.

🧩 Authentication Stack

Django Authentication

Custom User Model (users.User)

Google OAuth 2.0 via social_django

🔹 Supported Login Methods

Email & password

Google OAuth (Social Login)

Supported roles:

Student

Instructor


🤖 AI / RAG / Chatbot


AI Chatbot for interactive learning support

Video → text transcription using Whisper

PDF content ingestion

Vector store–based retrieval

Context-aware quiz generation

Cached embeddings for fast regeneration

Conversational AI powered by retrieved course content


🧱 Tech Stack


| Layer    | Technology                                |
| -------- | ----------------------------------------- |
| Backend  | Django 5.2+, FastAPI                      |
| Database | MySQL                                     |
| AI       | OpenAI/Ollama, DSPy, RAG, Whisper       |
| Auth     | Django Auth, Google OAuth (social_django) |
| Frontend | HTML, CSS, Bootstrap, JavaScript          |
| Media    | FFmpeg                                    |
| Language | Python 3.10+ (tested on 3.13)             |



📁 Project Structure


BILDUNG/

│

├── .venv/                         # Python virtual environment

│

├── core/                          # Django project core (global configuration)

│   ├── settings.py                # Main Django settings

│   ├── urls.py                    # Root URL routing

│   ├── asgi.py                    # ASGI entry point (async + WebSockets)

│   ├── wsgi.py                    # WSGI entry point

│   ├── middleware.py              # Global middleware

│   ├── hosts.py                   # Host-based routing (if enabled)

│   ├── management/                # Custom Django management commands

│   └── utils/                     # Shared utilities/helpers

│

├── users/                         # Authentication \& user management

│

├── courses/                       # Course \& learning management

│   ├── migrations/

│   ├── services/                  # Course business logic \& helpers

│   ├── static/                    # JS/CSS for course builder

│   ├── templates/                 # Course, instructor \& student templates

│   ├── models.py                  # domain driven models

│   ├── views.py                   # Course CRUD \& dashboards

│   ├── instructor_urls.py         # Instructor-specific routes

│   ├── student_urls.py            # Student-specific routes

│   ├── forms.py                   # Course \& module forms

│   ├── middleware.py              # Course access control

│   ├── signals.py                 # Progress tracking \& triggers

│   ├── utils.py                   # Reusable helpers

│   └── admin.py                   # Admin registrations

│

├── quizzes/                       # Quiz UI \& attempt handling (Django)

│

├── chat/                          # AI Chatbot (Django side)

│

├── forums/                        # Course discussion forums

│

├── home/                          # Public \& landing pages

│

├── fastapi_app/                   # AI services (FastAPI)

│   ├── config.py                  # FastAPI app configuration

│   ├── main_app.py                # FastAPI entry point

│   ├── database.py                # DB connection (FastAPI side)

│   ├── dependencies.py            # Dependency injection

│   │

│   ├── routes/                    # API endpoints

│   │   ├── ai_assist.py            # AI chatbot endpoints

│   │   ├── quiz_rag.py             # AI quiz generation endpoints

│   │   └── quiz.py.py             

│   │

│   ├── rag/                       # RAG implementation

│   │   ├── vector_store.py         # Embeddings \& vector storage

│   │   ├── cache.py                # Vector store caching

│   │   ├── loaders.py              # PDF \& video loaders

│   │   └── chunking.py             # Text chunking logic

│   │

│   ├── services/                    # AI service layer

│   │   ├── quiz_access.py          # quiz accessible lectures

│   │   └── rag_agent.py            # LLM calls & prompts for ai assist

│   │

│   └── models/                    # Request/response schemas

│

├── media/                         # Uploaded \& generated files

│   ├── lectures/

│   │   ├── videos/                # Uploaded lecture videos

│   │   └── files/                 # Uploaded PDFs

│   ├── Q_A/                       # question and answers excel sheets for ai_assist

│   └── resumes/                   # Uploaded resumes (if enabled)

│

├── rag_cache/                     # Cached vector stores (auto-generated)

│

├── .env                           # Environment variables (ignored)

├── .gitignore

├── manage.py                      # Django entry point

├── requirements.txt               # Python dependencies

├── pyproject.toml                 # Tooling \& project metadata

├── urls.py                        # Root URL mapping (project-level)

├── uv_setup.md                    # Uvicorn / FastAPI setup notes

└── README.md                      # Project documentation


⚙️ Step-by-Step Setup Guide


1️⃣ Clone the Repository


git clone https://github.com/your-username/bildung.git

cd bildung


2️⃣ Create Virtual Environment


Windows

python -m venv .venv

.venv\Scripts\activate


macOS / Linux

python3 -m venv .venv

source .venv/bin/activate


3️⃣ Install Python Dependencies


pip install --upgrade pip

pip install -r requirements.txt


4️⃣ Install System Dependencies


🔹 FFmpeg (Required for Whisper)

Windows

Download from https://ffmpeg.org/download.html

Extract (e.g. C:\ffmpeg)

Add C:\ffmpeg\bin to System PATH

Verify:

ffmpeg -version


macOS

brew install ffmpeg


Linux

sudo apt install ffmpeg


5️⃣  Environment Variables

Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key

⚠️ Never commit .env to GitHub.


6️⃣ Database Setup (MySQL)

Django Configuration in settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bildung_db',
        'USER': 'root',         # change with your MYSQL username
        'PASSWORD': 'your_mysql_password', 
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


In mysql shell, run

CREATE DATABASE bildung_db;

Then run:

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser



7️⃣ ⚙️ Google OAuth Setup

1️⃣ Create Google OAuth Credentials

1. Go to Google Cloud Console
   👉 https://console.cloud.google.com/

2. Create a new project (or select an existing one)

3. Configure OAuth Consent Screen

   User Type: External

   Scopes:
    email
    profile

   Add test users (for development)

4. Go to APIs & Services → Credentials

5. Click Create Credentials → OAuth Client ID

6. Choose Web Application


2️⃣ Configure Authorized Redirect URI

Add this redirect URI in Google Console:

http://127.0.0.1:8000/complete/google-oauth2/

⚠️ This must match exactly or Google login will fail.

For production:

https://your-domain.com/complete/google-oauth2/

 
3️⃣ Django Configuration 


INSTALLED_APPS += [
    'django.contrib.sites',
    'social_django',
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your_google_client_id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_google_client_secret
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'prompt': 'select_account',
    'access_type': 'offline',
}

SITE_ID = 1

4️⃣ Authentication Flow

User clicks "Continue with Google"
   ↓
Redirected to Google OAuth
   ↓
User grants permission
   ↓
Google returns profile data
   ↓
User is created or authenticated
   ↓
Redirected to dashboard


Existing users are matched by email

Duplicate accounts are prevented

Instructor login still respects email verification rules

🔒 Security Notes

OAuth tokens are handled server-side only

Secrets must be stored in .env

.env, media/, and rag_cache/ must never be committed

Google login users are mapped to the internal User model

🧪 Testing Google Login (Local)

Start Django:

python manage.py runserver


Visit:

http://127.0.0.1:8000/login/


Click Continue with Google

Select your Google account


8️⃣ Required Directories


Ensure these directories exist:

mkdir -p media/lectures/videos

mkdir -p media/lectures/files

mkdir rag_cache


NOTE - rag_cache/ is auto-generated and must not be committed.



▶️ Running the Project


🔹 Start the Application (Django + FastAPI + AI)

python manage.py runserver

Runs everything on:

http://127.0.0.1:8000/


🔹 Available Services

| Service                | URL                                                 |
| ---------------------- | --------------------------------------------------- |
| Django Web App         | `http://127.0.0.1:8000/`                            |
| AI Assistant           | `http://127.0.0.1:8000/api/ai/ask`                  |
| AI Quiz Generation     | `http://127.0.0.1:8000/api/quiz/{quiz_id}/generate` |
| FastAPI Docs           | `http://127.0.0.1:8000/api/docs`                    |


🧠 RAG Workflow


Video / PDF
  
    ↓

Whisper (video → text)

    ↓

Text Chunking

    ↓

Embeddings

    ↓

Vector Store (cached)

    ↓

Context Retrieval

    ↓

AI Response / Quiz


📡 Quiz Generation API


Endpoint

POST /quiz/{quiz_id}/generate


| Param  | Value              |

| ------ | ------------------ |

| scope  | all_before         |

| source | video / pdf / both |

| mode   | auto               |


Example

POST /quiz/5/generate?scope=all_before\&source=both\&mode=auto


📡 AI Assist API

POST /ai/ask

Request
{
  "question": "How do I enroll in a course?"
}

Response
{
  "answer": "To enroll, open the course page and click Enroll.",
  "category": "platform",
  "context_used": true
}


🧠 RAG Cache


Vector stores cached in rag_cache/

Filenames sanitized for Windows compatibility

Clear cache if lecture content changes:

rm -rf rag_cache


🛠️ Common Issues & Fixes


| Issue                        | Fix                           |

| ---------------------------- | ----------------------------- |

| ffmpeg not found             | Add FFmpeg to PATH            |

| Invalid argument `rag_cache` | Filename sanitization enabled |

| Slow AI response             | Whisper running on CPU        |

| Chatbot incorrect answers    | Clear RAG cache               |


🔐 Email Verification


User accounts start inactive

Verification token sent via email

Account activates after verification


🧪 Development Notes


Run Django and FastAPI in parallel

Restart FastAPI after .env changes

Use browser DevTools for JS debugging

Clear rag_cache/ when testing new content


🧩 Django Apps Overview


core: Contains global Django configuration including settings, middleware, and core utilities.

users: Handles user authentication, authorization, profiles, and role-based access (Admin, Instructor, Student).

courses: Manages course creation, modules, lectures, enrollment, and student progress tracking.

quizzes: Implements quizzes, questions, answers, scoring, and evaluations.

forums: Enables discussion boards for student and instructor communication.

chat: Provides real-time or internal messaging functionality.

home: Manages landing pages, dashboards, and general navigation views.


🚀 Future Improvements


Docker support

GPU acceleration

Payments

Multi-language Whisper

Streaming transcription


🤝 Contributing


We welcome contributions to Bildung!
Whether it’s a bug fix, new feature, documentation improvement, or AI enhancement — your help is appreciated.


Please follow the guidelines below to ensure smooth collaboration and code quality.

1️⃣ Fork the Repository

Click the Fork button on GitHub to create your own copy of the repository.

Then clone your fork locally:

git clone https://github.com/<your-username>/bildung.git

cd bildung


2️⃣ Create a Feature Branch

Always create a new branch for your work.

Do not work directly on the main branch.

git checkout -b feature/<short-feature-name>

Examples:

feature/ai-chat-improvements

bugfix/quiz-generation-error


3️⃣ Set Up the Development Environment

Ensure your environment is correctly configured:

python -m venv .venv

source .venv/bin/activate   # macOS/Linux

.venv\Scripts\activate      # Windows

pip install -r requirements.txt

Also ensure:

FFmpeg is installed and added to PATH

.env file is configured (do not commit it)

Django and FastAPI servers run successfully


4️⃣ Make Your Changes

Follow the existing project structure and conventions:

Django logic → inside respective apps (courses, users, quizzes, etc.)

AI / RAG logic → inside fastapi_app/

Frontend (JS/CSS/templates) → inside app-specific static/ and templates/

Business logic → prefer services/ over views

Signals & side effects → use signals.py

⚠️ Avoid:

hardcoding secrets

committing .env, media/, or rag_cache/


5️⃣ Run Tests & Verify Locally

Before committing, verify:

python manage.py check

python manage.py runserver

uvicorn fastapi_app.config:app --reload --port 8001


If you modify AI features:

Clear RAG cache:

rm -rf rag_cache

Test quiz generation and chatbot responses


6️⃣ Commit Your Changes

Write clear, meaningful commit messages:

git add .

git commit -m "Add AI chatbot context handling for course content"

Describe what and why


7️⃣ Push to Your Fork

git push origin <feature-name>

8️⃣ Open a Pull Request (PR)

Go to your fork on GitHub

Click Compare & Pull Request

Select:

Base branch: main

Compare branch: your feature branch

Fill in the PR description:

What was changed

Why it was changed

How it was tested


🔍 Code Review Process

Maintainers will review your PR

You may be asked to:

refactor code

add comments

fix edge cases

Once approved, your PR will be merged 🎉

