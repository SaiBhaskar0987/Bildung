from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from fastapi_app.dependencies import get_db
from fastapi_app.models.quiz import QuizChoice, QuizQuestion


router = APIRouter(prefix="/quiz", tags=["Quiz Manual"])

@router.post("/{quiz_id}/questions/manual")
def add_manual_question(
    quiz_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    question = QuizQuestion(
        quiz_id=quiz_id,
        question_text=payload["question_text"],
        options=payload["options"],
        correct_answer=payload["correct_answer"],
        is_auto_generated=False
    )
    db.add(question)
    db.flush()

    for key, text in payload["options"].items():
        db.add(
            QuizChoice(
                question_id=question.id,
                text=text,
                is_correct=(key == payload["correct_answer"])
            )
        )

    db.commit()
    return {"status": "success"}
