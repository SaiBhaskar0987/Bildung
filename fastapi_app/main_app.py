from fastapi import FastAPI
from fastapi_app.dependencies import get_db
from fastapi_app.routes import quiz, quiz_manual, quiz_rag, ai_assist
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
import os

load_dotenv() 

print("OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))


app = FastAPI(title="Bildung API")

@app.get("/")
def root():
    return {"message": "Bildung FastAPI is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz.router) 
app.include_router(quiz_rag.router)
app.include_router(quiz_manual.router)
app.include_router(ai_assist.router)


# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "OK"}

@app.get("/")
def api_root():
    return {
        "status": "ok",
        "service": "FastAPI running inside Django",
    }
