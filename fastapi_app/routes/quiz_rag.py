
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from fastapi_app.dependencies import get_db
from fastapi_app.rag.validator import validate_answer
from fastapi_app.rag.vector_store import get_or_create_vector_store
from fastapi_app.rag.question_generator import generate_questions
from fastapi import Body


router = APIRouter(prefix="/quiz", tags=["Quiz RAG"])
@router.post("/{quiz_id}/generate")
def generate_quiz(
    quiz_id: int,
    scope: str = Query("all_before"),
    mode: str = Query("auto"),
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
):
    
    if mode == "manual":
        return {
            "quiz_id": quiz_id,
            "mode": "manual",
            "questions": [],
        }

    try:
        num_questions = int(payload.get("num_questions", 5))
    except (TypeError, ValueError):
        num_questions = 5

    num_questions = max(1, min(num_questions, 50))

    vector_store = get_or_create_vector_store(
        quiz_id=quiz_id,
        scope=scope,
        db=db,
    )

    if not vector_store:
        return {
            "quiz_id": quiz_id,
            "mode": "auto",
            "scope": scope,
            "questions": [],
            "warning": "No lecture content available",
        }

    questions = generate_questions(
        vector_store,
        num_questions=num_questions,
    )
    print("🧠 Generating", num_questions, "questions")


    if not questions:
        return {
            "quiz_id": quiz_id,
            "mode": "auto",
            "scope": scope,
            "questions": [],
            "warning": "AI could not generate valid questions",
        }

    return {
        "quiz_id": quiz_id,
        "mode": "auto",
        "scope": scope,
        "num_questions": num_questions,
        "questions": questions,
    }

@router.post("/{quiz_id}/validate-answer")
def validate_quiz_answer(
    quiz_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    vector_store = get_or_create_vector_store(quiz_id, db)

    question = payload.get("question")
    student_answer = payload.get("answer")

    if not question or not student_answer:
        raise HTTPException(
            status_code=400,
            detail="Both question and answer are required"
        )

    result = validate_answer(
        vector_store,
        question,
        student_answer
    )

    return {
        "quiz_id": quiz_id,
        "result": result
    }

