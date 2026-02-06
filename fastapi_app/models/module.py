from sqlalchemy import Column, Integer, String
from fastapi_app.database import Base

class Module(Base):
    __tablename__ = "courses_module"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer)
    title = Column(String(255))
    module_order = Column(Integer)
