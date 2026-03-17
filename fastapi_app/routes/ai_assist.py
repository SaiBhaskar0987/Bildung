from fastapi import APIRouter
from pydantic import BaseModel
from fastapi_app.services.rag_agent import ClassifierAgent

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
    return AskResponse(
        answer=answer,
        category=category,
        context_used=context_used
    )
