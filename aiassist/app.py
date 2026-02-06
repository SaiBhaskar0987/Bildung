from fastapi import FastAPI
from pydantic import BaseModel
from aiassist.rag_agent import ClassifierAgent

app = FastAPI(title="AI Assist API", description="FastAPI for AI model calls")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    category: str
    context_used: bool

agent = ClassifierAgent()

@app.post("/ask", response_model=AskResponse)
def ask_ai(request: AskRequest):
    """
    Endpoint to query the AI model.
    Expects a JSON payload: {"question": "your question here"}
    """
    answer, category, context_used = agent(request.question)
    return AskResponse(answer=answer, category=category, context_used=context_used)