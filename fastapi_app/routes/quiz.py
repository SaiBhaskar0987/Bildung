from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi_app.dependencies import get_db
from fastapi_app.services.quiz_access import get_accessible_lectures_for_quiz

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)


@router.get("/{quiz_id}/lectures")
def quiz_accessible_lectures(
    quiz_id: int,
    scope: str = Query("all_before"),   
    db: Session = Depends(get_db),
):
    return get_accessible_lectures_for_quiz(
        quiz_id=quiz_id,
        scope=scope,
        db=db,
    )