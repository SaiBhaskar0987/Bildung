from sqlalchemy.orm import Session
from fastapi import HTTPException

from fastapi_app.models.quiz import Quiz
from fastapi_app.models.course import Course
from fastapi_app.models.lecture import Lecture


def normalize_scope(scope: str | None) -> str:
    if scope in (None, "", "all", "all_before"):
        return "all_before"

    if scope in ("between", "since", "since_last_quiz"):
        return "since_last_quiz"

    raise HTTPException(
        status_code=400,
        detail=f"Invalid scope: {scope}"
    )


def get_accessible_lectures_for_quiz(
    quiz_id: int,
    scope: str,
    db: Session
):
    scope = normalize_scope(scope)

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    course = db.query(Course).filter(Course.id == quiz.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    structure = course.structure_json or []

    current_quiz_index = None
    for i, item in enumerate(structure):
        if item.get("type") == "Quiz" and str(item.get("quiz_id")) == str(quiz_id):
            current_quiz_index = i
            break

    if current_quiz_index is None:
        current_quiz_index = len(structure)

    previous_quiz_index = -1
    for i in range(current_quiz_index - 1, -1, -1):
        if structure[i].get("type") == "Quiz":
            previous_quiz_index = i
            break

    module_ids: list[int] = []

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

    if not module_ids and scope != "all_before":

        for index, item in enumerate(structure):
            if item.get("type") == "Module" and index < current_quiz_index:
                if item.get("module_id"):
                    module_ids.append(int(item["module_id"]))

    if not module_ids:
        print("DEBUG → no modules found for quiz")
        return []

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

    pdfs = []
    for lecture in lectures:
        file = getattr(lecture, "file", None)

        if isinstance(file, str) and file.strip():
            pdfs.append(file)

        print(
            f"DEBUG → Lecture {lecture.id} | "
            f"raw_file={repr(file)}"
        )

    return pdfs


def get_quiz_videos(
    quiz_id: int,
    scope: str,
    db: Session
):
    lectures = get_accessible_lectures_for_quiz(
        quiz_id,
        scope,
        db
    )

    videos = []
    for lecture in lectures:
        video = getattr(lecture, "video", None)

        if isinstance(video, str) and video.strip():
            videos.append(video)

        print(
            f"DEBUG → Lecture {lecture.id} | "
            f"raw_video={repr(video)}"
        )

    return videos
