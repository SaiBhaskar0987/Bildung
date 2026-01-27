from sqlalchemy import Column, Integer, String, JSON
from fastapi_app.database import Base

class Course(Base):
    __tablename__ = "courses_course"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    structure_json = Column(JSON)





