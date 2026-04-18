from sqlalchemy import Column, String
from app.database import Base
import uuid


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    description = Column(String, nullable=False)
    priority = Column(String, default="medium")
    status = Column(String, default="pending")
    result = Column(String, nullable=True)

    def __repr__(self):
        return f"<Task(id={self.id}, description={self.description}, priority={self.priority}, status={self.status})>"