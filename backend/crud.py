from http.client import HTTPException
import models
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import User, Project
from schemas import ProjectBase, UserCreate, ProjectCreate, ProjectUpdate
from auth import get_password_hash
from models import ChatStateModel
from schemas import ChatStateCreate
from datetime import datetime

def get_user_by_username(db: Session, username: str): #, organization: str
    return db.query(User).filter(User.username == username).first() #and_( , User.organization == organization


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password, organization=user.organization)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_project(db: Session, project: ProjectCreate, user_id: int):
    db_project = Project(**project.dict(), user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project



# Utility function
def get_project(db: Session, project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def get_projects_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: int, project: ProjectUpdate):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        return None
    for key, value in project.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project



# Chat STate
def create_or_update_chat_state(db: Session, chat_state: ChatStateCreate):
    existing_state = db.query(ChatStateModel).filter(
        ChatStateModel.project_id == chat_state.project_id,
        ChatStateModel.solution_name == chat_state.solution_name
    ).first()

    if existing_state:
        existing_state.messages = chat_state.messages
        existing_state.updated_at = datetime.utcnow()
    else:
        new_state = ChatStateModel(
            project_id=chat_state.project_id,
            solution_name=chat_state.solution_name,
            messages=chat_state.messages
        )
        db.add(new_state)

    db.commit()
    return existing_state or new_state

def get_chat_state(db: Session, project_id: int, solution_name: str):
    return db.query(ChatStateModel).filter(
        ChatStateModel.project_id == project_id,
        ChatStateModel.solution_name == solution_name
    ).first()

# Project

def find_project(db: Session, project_id: int, user_id: int):
    project = db.query(models.Project).filter(
        models.Project.id == project_id, 
        models.Project.user_id == user_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

def update_project(db: Session, project_id: int, project: ProjectBase, user_id: int):
    db_project = db.query(models.Project).filter(
        models.Project.id == project_id, 
        models.Project.user_id == user_id
    ).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.name = project.name
    db_project.description = project.description
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int, user_id: int):
    db_project = db.query(models.Project).filter(
        models.Project.id == project_id, 
        models.Project.user_id == user_id
    ).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"detail": "Project deleted successfully"}