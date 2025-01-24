from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class ChatStateModel(Base):
    __tablename__ = "chat_states"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    solution_name = Column(String, nullable=False)
    messages = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    organization = Column(String)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    environment_spec = Column(Text, nullable=True)
    system_spec = Column(Text, nullable=True)
    safety_property = Column(Text, nullable=True)
    config = Column(JSON, nullable=True)

    user = relationship("User", back_populates="projects")



User.projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
