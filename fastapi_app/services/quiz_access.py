from sqlalchemy.orm import Session
from fastapi import HTTPException

from fastapi_app.models.quiz import Quiz
from fastapi_app.models.course import Course
from fastapi_app.models.lecture import Lecture


def get_accessible_lectures_for_quiz(
    quiz_id: int,
    scope: str,
    db: Session
):

    print("DEBUG → scope received:", scope)

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    course = db.query(Course).filter(Course.id == quiz.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    structure = course.structure_json or []

    current_quiz_index = None
    for i, item in enumerate(structure):
        if (
            item.get("type") == "Quiz"
            and str(item.get("quiz_id")) == str(quiz_id)
        ):
            current_quiz_index = i
            break

    if current_quiz_index is None:
        current_quiz_index = len(structure)

    previous_quiz_index = -1
    for i in range(current_quiz_index - 1, -1, -1):
        if structure[i].get("type") == "Quiz":
            previous_quiz_index = i
            break

    if scope in (None, "", "all", "all_before"):
        scope = "all_before"
    elif scope in ("between", "since", "since_last_quiz"):
        scope = "since_last_quiz"

    module_ids = []

    for index, item in enumerate(structure):
        if item.get("type") != "Module":
            continue

        module_id = item.get("module_id")
        if not module_id:
            continue

        module_id = int(module_id)  

        if scope == "all_before" and index < current_quiz_index:
            module_ids.append(module_id)

        elif scope == "since_last_quiz" and previous_quiz_index < index < current_quiz_index:
            module_ids.append(module_id)

    if not module_ids:
        for index, item in enumerate(structure):
            if item.get("type") == "Module" and index < current_quiz_index:
                if item.get("module_id"):
                    module_ids.append(int(item["module_id"]))

    return (
        db.query(Lecture)
        .filter(Lecture.module_id.in_(module_ids))
        .order_by(Lecture.module_id, Lecture.lecture_order)
        .all()
    )


def get_quiz_pdfs(
    quiz_id: int,
    scope: str,
    db: Session
):
    lectures = get_accessible_lectures_for_quiz(
        quiz_id,
        scope,
        db
    )

    return [
        lecture.file
        for lecture in lectures
        if lecture.file
    ]
