from sqlalchemy import Column, Integer, String
from fastapi_app.database import Base
from sqlalchemy import (Column, Integer, String, Text, Boolean,DateTime, ForeignKey, JSON, func)
from sqlalchemy.orm import relationship

class Quiz(Base):
    __tablename__ = "quizzes_quiz"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer)
    title = Column(String(255))
    quiz_order = Column(Integer)


class QuizQuestion(Base):
    __tablename__ = "quizzes_quizquestion"

    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes_quiz.id", ondelete="CASCADE"))

    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)

    correct_answer = Column(String(1), nullable=False)
    is_auto_generated = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())

    choices = relationship(
        "QuizChoice",
        back_populates="question",
        cascade="all, delete"
    )


class QuizChoice(Base):
    __tablename__ = "quizzes_quizchoice"

    id = Column(Integer, primary_key=True)
    question_id = Column(
        Integer,
        ForeignKey("quizzes_quizquestion.id", ondelete="CASCADE")
    )

    text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship("QuizQuestion", back_populates="choices")
