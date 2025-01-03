from http.client import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import User, Project
from schemas import UserCreate, ProjectCreate, ProjectUpdate
from auth import get_password_hash


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
