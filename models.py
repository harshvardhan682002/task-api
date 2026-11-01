from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Task(Base):
    __tablename__ = "tasks"                          # table name

    id = Column(Integer, primary_key=True, index=True)   # unique number, set automatically
    title = Column(String, nullable=False)               # text, required
    done = Column(Boolean, default=False)                # true/false