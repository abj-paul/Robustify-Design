from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, Project
from schemas import UserCreate, ProjectCreate, Project, SpecModel, LoginRequest
from auth import create_access_token, verify_password
import crud
from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from typing import Optional
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
import httpx
from typing import List
from fastapi.responses import JSONResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()
# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PIPELINE_SERVER_ADDRESS = "http://localhost:8000"
BASE_PROJECT_FOLDER = "projects"

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username): #, user.organization
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db, user)


@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, request.username)
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": create_access_token({"sub": request.username}), "user": user}



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

    spec_filename = "env.lts" if file and file.filename.endswith("lts") else "env.xml"
    return await handle_specification_upload(project, file, content, spec_filename)


@app.get("/projects/{project_id}/environment_spec")
async def get_environment_spec(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    return {"environment_spec": project.environment_spec}


@app.put("/projects/{project_id}/environment_spec")
async def update_environment_spec(project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project.environment_spec = (await file.read()).decode("utf-8") if file else content
    db.commit()
    
    spec_filename = "env.lts" if file and file.filename.endswith("lts") else "env.xml"
    return await handle_specification_upload(project, file, content, spec_filename)



# System Specification Endpoints
@app.post("/projects/{project_id}/system_spec")
async def upload_system_spec(
    project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    project.system_spec = (await file.read()).decode("utf-8") if file else content
    db.commit()
    
    spec_filename = "sys.lts"
    if file: spec_filename = "sys.lts" if file and file.filename.endswith("lts") else "sys.xml"
    else: spec_filename = "sys.xml" if "uml" in content else "sys.lts"

    return await handle_specification_upload(project, file, content, spec_filename)


@app.get("/projects/{project_id}/system_spec")
async def get_system_spec(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    return {"system_spec": project.system_spec}

@app.put("/projects/{project_id}/system_spec")
async def update_system_spec(project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.system_spec = (await file.read()).decode("utf-8") if file else content
    db.commit()
    spec_filename = "sys.xml" if content and "uml" in content else "sys.lts"
    return await handle_specification_upload(project, file, content, spec_filename)
    


# Safety Property Endpoints
@app.post("/projects/{project_id}/safety_spec")
async def upload_safety_property(
    project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    project.safety_property = (await file.read()).decode("utf-8") if file else content
    db.commit()

    spec_filename = "p.xml" if content and "uml" in content else "p.lts"
    return await handle_specification_upload(project, file, content, spec_filename)


@app.get("/projects/{project_id}/safety_spec")
async def get_safety_property(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    return {"safety_property": project.safety_property}


@app.put("/projects/{project_id}/safety_spec")
async def update_safety_property(project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project.safety_property = (await file.read()).decode("utf-8") if file else content
    db.commit()
    
    spec_filename = "p.xml" if content and "uml" in content else "p.lts"
    return await handle_specification_upload(project, file, content, spec_filename)


# Configuration File Endpoints
@app.post("/projects/{project_id}/configuration_spec")
async def upload_config(project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    content = (await file.read()).decode("utf-8") if file else content
    try:
        project.config = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in config file")
    db.commit()
    
    spec_filename = "config-pareto.json"
    return await handle_specification_upload(project, file, content, spec_filename)


@app.get("/projects/{project_id}/configuration_spec")
async def get_config(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    return {"config": project.config}


@app.put("/projects/{project_id}/configuration_spec")
async def update_config(project_id: int, file: UploadFile = None, content: Optional[str] = Form(None), db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project.config = (await file.read()).decode("utf-8") if file else content
    db.commit()
    spec_filename = "config-pareto.json"
    return await handle_specification_upload(project, file, content, spec_filename)

# Robustification
@app.post("/projects/{project_id}/execute")
async def run_fortis(
    project_id: int,
    class_list: List[str] = Form(...),
    db: Session = Depends(get_db)
):
    project = crud.get_project(db, project_id)
    project_folder = f"{BASE_PROJECT_FOLDER}/{project.name}-{project.id}"

    timeout = httpx.Timeout(60.0)  # Adjust timeout as needed (e.g., 60 seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{PIPELINE_SERVER_ADDRESS}/execute",
            data={"project_folder": project_folder, "class_list": class_list}
        )
    
    if response.status_code == 200:
        return JSONResponse(content=response.json(), status_code=response.status_code)
    else:
        return JSONResponse(
            content={"error": response.text}, status_code=response.status_code
        )



# Services
@app.get("/service/uml-to-png")
async def generate_image(umlContent: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(PIPELINE_SERVER_ADDRESS + "/service/xml-to-png", params={"xmlContent": umlContent})
            response.raise_for_status()
            return response.json()  # Assuming the target service returns JSON
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error: {str(e)}")


@app.post("/service/lts-to-png")
async def update_environment_spec(project_id: int, spec: SpecModel, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project.environment_spec = spec.content
    db.commit()
    return {"message": "Environment spec updated successfully"}


async def handle_specification_upload(project, file, content, spec_filename):
    project_folder = f"{BASE_PROJECT_FOLDER}/{project.name}-{project.id}"
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PIPELINE_SERVER_ADDRESS}/create_project/", data={"project_name":f"{project.name}-{project.id}", "project_description": project.description})

        if file:  
            files = {"files": (file.filename, file.file, file.content_type)}
            response = await client.post(
                f"{PIPELINE_SERVER_ADDRESS}/upload/files",
                data={"project_folder": project_folder},
                files=files
            )
        else:  
            response = await client.post(
                f"{PIPELINE_SERVER_ADDRESS}/upload/specification/",
                data={
                    "filename": f"{spec_filename}",
                    "specification": content,
                    "project_folder": project_folder
                }
            )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to upload specification")

    #return {"message": "System spec updated successfully in database and file"}

    return {"message": f"{spec_filename} spec saved successfully in {project_folder}."}