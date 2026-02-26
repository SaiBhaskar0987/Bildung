📚 Bildung – AI-Powered E-Learning Platform

    Bildung is a full-stack e-learning platform that combines Django for core application logic and FastAPI for AI-powered features such as quiz generation, an AI learning chatbot using RAG (Retrieval-Augmented Generation).
    
    The platform supports instructors and students, structured courses, modules, quizzes, assessments, video/PDF content, dashboards, and personalized recommendations and conversational AI assistance.


🚀 Features:

👨‍🏫 Instructor

    Instructors can sign up using email or Google, verify their accounts, and create, edit, and publish courses using a structured course builder with modules, quizzes, assessments, live classes, and video/PDF lectures. A dedicated instructor dashboard helps manage courses and track overall teaching activity.


👨‍🎓 Student

    Students can register via email or Google, verify their accounts, enroll in courses, and track their learning progress through a personalized dashboard. The platform offers AI-generated and manual quizzes, assessments, an AI chatbot for learning support, personalized recommendations, and course completion certificates.


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


🤖 AI

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
| AI       | OpenAI, Whisper                           |
| Auth     | Django Auth, Google OAuth (social_django) |
| Frontend | HTML, CSS, Bootstrap, JavaScript          |
| Media    | FFmpeg                                    |
| Language | Python 3.10+ (tested on 3.13)             |


📁 Project Structure

BILDUNG/

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

├── users/                         # Authentication & user management

├── courses/                       # Course & learning management

│   ├── migrations/

│   ├── services/                  # Course business logic & helpers

│   ├── static/                    # JS/CSS for course builder

│   ├── templates/                 # Course, instructor & student templates

│   ├── models.py                  # domain driven models

│   ├── views.py                   # Course CRUD & dashboards

│   ├── instructor_urls.py         # Instructor-specific routes

│   ├── student_urls.py            # Student-specific routes

│   ├── forms.py                   # Course \& module forms

│   ├── middleware.py              # Course access control

│   ├── signals.py                 # Progress tracking \& triggers

│   ├── utils.py                   # Reusable helpers

│   └── admin.py                   # Admin registrations

├── quizzes/                       # Quiz UI & attempt handling (Django)

├── chat/                          # AI Chatbot (Django side)

├── forums/                        # Course discussion forums

├── home/                          # Public & landing pages

├── fastapi_app/                   # AI services (FastAPI)

│   ├── config.py                  # FastAPI app configuration

│   ├── main_app.py                # FastAPI entry point

│   ├── database.py                # DB connection (FastAPI side)

│   ├── dependencies.py            # Dependency injection

│   ├── routes/                    # API endpoints

│   │   ├── ai_assist.py            # AI chatbot endpoints

│   │   ├── quiz_rag.py             # AI quiz generation endpoints

│   │   └── quiz.py.py             

│   ├── rag/                       # RAG implementation

│   │   ├── vector_store.py         # Embeddings \& vector storage

│   │   ├── cache.py                # Vector store caching

│   │   ├── loaders.py              # PDF \& video loaders

│   │   └── chunking.py             # Text chunking logic

│   ├── services/                    # AI service layer

│   │   ├── quiz_access.py          # quiz accessible lectures

│   │   └── rag_agent.py            # LLM calls & prompts for ai assist

│   └── models/                    # Request/response schemas

├── media/                         # Uploaded & generated files

│   ├── lectures/

│   │   ├── videos/                # Uploaded lecture videos

│   │   └── files/                 # Uploaded PDFs

│   ├── Q_A/                       # question and answers excel sheets for ai_assist

│   └── resumes/                   # Uploaded resumes (if enabled)

├── rag_cache/                     # Cached vector stores (auto-generated)

├── .env                           # Environment variables

├── manage.py                      # Django entry point

├── requirements.txt               # Python dependencies

├── pyproject.toml                 # Tooling & project metadata

├── urls.py                        # Root URL mapping (project-level)

├── uv_setup.md                    # Uvicorn / FastAPI setup notes

└── README.md                      # Project documentation

📋 Prerequisites

    To run this project in Visual Studio Code, ensure that Python 3.11 or higher is installed on your system and accessible from the power shell. A package manager (pip) must be available, which is included with standard Python installations.

    The project requires Git to clone the repository and manage source control. For database functionality, a running MySQL server is required with valid credentials.

    verify that Python 3.11 or higher is installed and accessible
        run the following command in VS code terminal:
            - python --version

    🔑 Generate an OpenAI API Key

    To enable AI features such as quiz generation and the AI learning chatbot, you must create an OpenAI API key.

    Step 1: Visit OpenAI Platform

        Open the official OpenAI website:
        👉 https://platform.openai.com/

    Step 2: Sign In or Create an Account

        Log in using your email, Google, or Microsoft account.
        If you don’t have an account, complete the signup process.

    Step 3: Open the API Keys Page

        After logging in, go directly to the API Keys section:
        👉 https://platform.openai.com/api-keys

    Step 4: Create a New Secret Key

        Click “Create new secret key”.
        A new API key will be generated instantly.

    ⚠️ Important: Copy the key immediately and store it securely.
    You won’t be able to see this key again after closing the dialog.


⚙️ Setup guidelines for bildung

1️⃣ Clone the Repository(VS code terminal or git bash or CMD)

    - git clone https://github.com/SaiBhaskar0987/Bildung.git
    - cd bildung

2️⃣ Create Virtual Environment

    Windows(VSCode):
    Creating Virtual Environment:
        - python -m venv .venv
    Activating Virtual Environment:
        - .venv\Scripts\activate

    macOS / Linux
    Creating Virtual Environment:
        - python3 -m venv .venv
    Activating Virtual Environment:
        - source .venv/bin/activate

3️⃣ Install Python Dependencies

    - pip install -r requirements.txt

4️⃣ Install System Dependencies

    FFmpeg (Required for Whisper)
    Windows 
    1. Download from the url: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    2. Extract the zip folder, copy the bin path
    3. Add your bin path to environment variables, system variables, path
    4. New -> paste your path -> ok
    5. Verify you ffmpeg enabled correctly:
            - Go to cmd(Command Prompt)
            - Type command - 'ffmpeg -version'
            - Then you will see the content same as in the attached image

            ![ffmpeg](media/ffmpeg_verification.png)

5️⃣  Environment Variables

    Create a .env file in the project root:
    Copy the below text and paste in .env
        API_KEY = paste your secret key here
    ⚠️ Note: Never commit .env to GitHub.


6️⃣ Database Setup (MySQL):

    1. Go to core/settings.py.
    2. Go to DATABASES variable, update your database user and password.
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'bildung_db',
                'USER': 'your_user_name',         # change with your MYSQL username
                'PASSWORD': 'your_mysql_password', # change with your MYSQL password
                'HOST': 'localhost',
                'PORT': '3306',
                'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            }
        }

7️⃣ ⚙️ Google OAuth Setup:

    1. Create Google OAuth Credentials
        - https://console.cloud.google.com/
    2. Click on select project -> New project (or select an existing one)
         Enter Project_Name
         Organisation(Depends on you)
    3. Go to APIs & Services -> OAuth Consent Screen
        Get started -> Fill you project details
            - App Information
            - Audience: External
            - Contact Information
            - Finish -> Create
    4. Go home -> APIs & Services -> Credientials -> Create Credientials -> Outh client id
        1. Application type: Web application
        2. Add below url in Authoriseed Javascript Origin's
        ⚠️ Note: This must match exactly or Google login will fail.
            - http://127.0.0.1:8000/
        3. Add below urls in Authorised Redirect URL's
        ⚠️ Note: This must match exactly or Google login will fail.
            - http://127.0.0.1:8000/complete/google-oauth2/
            - http://127.0.0.1:8000/login/google-oauth2/
        4. Press create
        5. Copy your Client ID and Client Secret
        **For production**:
            for production follow the same above steps with your new url's.
            Ex: https://your-domain.com/complete/google-oauth2/
    5. Go back to your app(Bildung):
        Go to core/settings.py,
            Update you Client ID and Clent Secret at below variables.
                    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your_google_client_id'
                    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your_google_client_secret'
        
8️⃣ Run the Django Server:

    Go to Vscode terminal ans paste the below commands:

    - python manage.py makemigrations
    - python manage.py migrate
    - python manage.py runserver

    If you want to check admin status:

    - python manage.py createsuperuser

    Visit:
    
    http://127.0.0.1:8000/


Start Exploring

🔹 Available Services

| Service                      | URL                                                 | Description                          |
| ---------------------------- | --------------------------------------------------- | ------------------------------------ |
| **Django Web App**           | `http://127.0.0.1:8000/`                            | Main platform interface              |
| **Admin Login**              | `http://127.0.0.1:8000/accounts/admin/login/`       | Platform administrator login         |
| **Django Admin Panel**       | `http://127.0.0.1:8000/admin/`                      | Advanced database & model management |
| **AI Assistant API**         | `http://127.0.0.1:8000/api/ai/ask`                  | AI chatbot endpoint                  |
| **AI Quiz Generation API**   | `http://127.0.0.1:8000/api/quiz/{quiz_id}/generate` | Generate AI quizzes                  |
| **FastAPI Interactive Docs** | `http://127.0.0.1:8000/api/docs`                    | Explore & test AI endpoints          |


🔐 Admin Setup & Management

    Bildung includes a role-based administration system that allows platform administrators to manage users, courses, content, and platform operations.

    Unlike the default Django admin panel, Bildung provides an app-level admin interface accessible via:

    👉 http://127.0.0.1:8000/accounts/admin/login/

    Admins log in through the standard authentication system and are granted elevated privileges.

👤 Creating an Admin Account

    Before logging in as an admin, you must create a superuser.

    Option 1: Create Superuser
        Step 1: Run the Command
            - python manage.py createsuperuser
        Step 2: Provide Details

            You will be prompted to enter:

            Username
            Email address
            Password

            Example:

            Username: admin
            Email: admin@example.com
            Password: ********

            ⚠️ Password will be hidden while typing.


    Option 2: Create via Django Shell
        Run these commands in VS code terminal
            1. - python manage.py shell
            2. - from users.models import User

            3. - admin = User.objects.create_user(
                 username="admin",
                 email="admin@example.com",
                 password="admin123",
                 role="admin"
                 )

            4. admin.is_staff = True
            5. admin.is_superuser = True
            6. admin.save()

🔐 Admin Login

    🌐 Login URL

    👉 http://127.0.0.1:8000/accounts/admin/login/

    🪪 Steps

    1. Open the login page.
    2. Enter admin email/username & password.
    3. Click Login.

    You will be redirected to the admin dashboard.


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

    Endpoint: 
    POST /quiz/{quiz_id}/generate

    ┌───────┬────────────────────┐
    │ Param │ Value              │
    ├───────┼────────────────────┤
    │ scope │ all_before         │
    │ source│ video / pdf / both │
    │ mode  │ auto               │
    └───────┴────────────────────┘

    Example:
    POST /quiz/5/generate?scope=all_before\&source=both\&mode=auto


📡 AI Assist API
    
    Endpoint: 
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

    - rm -rf rag_cache


🛠️ Common Issues & Fixes

    ┌──────────────────────┬──────────────────────────┐
    │ Issue                │ Fix                      │
    ├──────────────────────┼──────────────────────────┤
    │ ffmpeg not found     │ Add FFmpeg to PATH       │
    │ Invalid rag_cache    │ Enable filename sanitize │
    │ Slow AI response     │ Whisper on CPU           │
    │ Wrong chatbot answer │ Clear RAG cache          │
    └──────────────────────┴──────────────────────────┘


🔐 Email Verification

    User accounts start inactive

    Verification token sent via email

    Account activates after verification


🧪 Development Notes

    Restart the server after .env changes

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

        - git clone https://github.com/SaiBhaskar0987/Bildung.git
        - cd bildung

    2️⃣ Create a Feature Branch

       Always create a new branch for your work.

        Do not work directly on the main branch.

        git checkout -b feature/<short-feature-name>

        Examples:

           feature/ai-chat-improvements
            bugfix/quiz-generation-error

    3️⃣ Set Up the Development Environment

        Ensure your environment is correctly configured:

        - python -m venv .venv

        - source .venv/bin/activate   # macOS/Linux

        - .venv\Scripts\activate      # Windows

        - pip install -r requirements.txt

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

            - python manage.py check

            - python manage.py runserver

        If you modify AI features:

            Clear RAG cache:
            - rm -rf rag_cache

        Test quiz generation and chatbot responses


    6️⃣ Commit Your Changes

        Write clear, meaningful commit messages:

        - git add .

        - git commit -m "Add AI chatbot context handling for course content"

        Describe what and why

    7️⃣ Push to Your Fork

        - git push origin <feature-name>

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
