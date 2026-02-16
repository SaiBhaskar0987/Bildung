from fastapi import APIRouter
from pydantic import BaseModel
from fastapi_app.services.rag_agent import ClassifierAgent
from quizzes.models import UnansweredQuestion

router = APIRouter(prefix="/ai", tags=["AI Assist"])

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    category: str
    context_used: bool

agent = ClassifierAgent()

@router.post("/ask", response_model=AskResponse)
def ask_ai(request: AskRequest):
    answer, category, context_used = agent(request.question)
    if answer is None or answer.strip() == "" or "I don't know" in answer.lower():
        UnansweredQuestion.objects.create(
            question=request.question,
            user_id=request.user_id
        )
        return AskResponse(
            answer="Sorry, I don't have an answer for that right now. Your question has been forwarded to our team for review.",
            category="unanswered",
            context_used=False
        )
    return AskResponse(
        answer=answer,
        category=category,
        context_used=context_used
    )
