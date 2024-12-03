from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, Project
from schemas import UserCreate, ProjectCreate, Project, SpecModel
from auth import create_access_token, verify_password
import crud
from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from typing import Optional
import json

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": create_access_token({"sub": username})}


@app.get("/projects", response_model=list[Project])
def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    return crud.get_projects_by_user(db, user_id)


@app.post("/projects", response_model=Project)
def create_project(project: ProjectCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.create_project(db, project, user_id)


# Environment Specification Endpoints
@app.post("/projects/{project_id}/environment_spec")
async def upload_environment_spec(
    project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    project.environment_spec = (await file.read()).decode("utf-8") if file else content
    db.commit()
    return {"message": "Environment spec uploaded successfully"}


@app.get("/projects/{project_id}/environment_spec")
async def get_environment_spec(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    return {"environment_spec": project.environment_spec}


@app.put("/projects/{project_id}/environment_spec")
async def update_environment_spec(project_id: int, spec: SpecModel, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project.environment_spec = spec.content
    db.commit()
    return {"message": "Environment spec updated successfully"}


# Other endpoints (system_spec, safety_property, config) follow the same structure as above.
# ...



# System Specification Endpoints
@app.post("/projects/{project_id}/system_spec")
async def upload_system_spec(
    project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    project.system_spec = (await file.read()).decode("utf-8") if file else content
    db.commit()
    return {"message": "System spec uploaded successfully"}


@app.get("/projects/{project_id}/system_spec")
async def get_system_spec(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    return {"system_spec": project.system_spec}


@app.put("/projects/{project_id}/system_spec")
async def update_system_spec(project_id: int, spec: SpecModel, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project.system_spec = spec.content
    db.commit()
    return {"message": "System spec updated successfully"}


# Safety Property Endpoints
@app.post("/projects/{project_id}/safety_property")
async def upload_safety_property(
    project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    project.safety_property = (await file.read()).decode("utf-8") if file else content
    db.commit()
    return {"message": "Safety property uploaded successfully"}


@app.get("/projects/{project_id}/safety_property")
async def get_safety_property(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    return {"safety_property": project.safety_property}


@app.put("/projects/{project_id}/safety_property")
async def update_safety_property(project_id: int, spec: SpecModel, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project.safety_property = spec.content
    db.commit()
    return {"message": "Safety property updated successfully"}


# Configuration File Endpoints
@app.post("/projects/{project_id}/config")
async def upload_config(project_id: int, file: UploadFile, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    content = (await file.read()).decode("utf-8")
    try:
        project.config = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in config file")
    db.commit()
    return {"message": "Config file uploaded successfully"}


@app.get("/projects/{project_id}/config")
async def get_config(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    return {"config": project.config}


@app.put("/projects/{project_id}/config")
async def update_config(project_id: int, config: dict, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project.config = config
    db.commit()
    return {"message": "Config file updated successfully"}
