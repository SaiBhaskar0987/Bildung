from sqlalchemy import Column, Integer, String
from fastapi_app.database import Base

class Lecture(Base):
    __tablename__ = "courses_lecture"

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer)
    title = Column(String(255))
    video = Column(String)
    file = Column(String)
    lecture_order = Column(Integer)
