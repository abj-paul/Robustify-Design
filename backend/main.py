from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, Project
from schemas import ProjectBase, UserCreate, ProjectCreate, Project, SpecModel, LoginRequest
from auth import authenticate_request, create_access_token, verify_password
import crud
from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from typing import Optional
import json
from fastapi import HTTPException
import httpx
from typing import List
from fastapi.responses import JSONResponse
import os
from database import Base, engine
from models import ChatStateModel
from database import SessionLocal
from crud import create_or_update_chat_state, get_chat_state
from schemas import ChatStateCreate, ChatStateResponse
import models
from fastapi.middleware.cors import CORSMiddleware

PIPELINE_SERVER_ADDRESS = "http://localhost:8000"
BASE_PROJECT_FOLDER = "projects"


# Ensure tables are created on startup
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
#app.middleware("http")(authenticate_request)


# Routes
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db, user)


@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, request.username)
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {
        "access_token": create_access_token({"sub": request.username}),
        "user": user
    }

@app.get("/projects", response_model=list[Project])
def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    return crud.get_projects_by_user(db, user_id)


@app.post("/projects", response_model=Project)
def create_project(project: ProjectCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.create_project(db, project, user_id)

@app.get("/projects/{project_id}", response_model=Project)
def get_project(
    project_id: int, 
    user_id: int, 
    db: Session = Depends(get_db)
):
    return crud.get_project(db, project_id, user_id)

@app.put("/projects/{project_id}", response_model=Project)
def update_project(
    project_id: int, 
    project: ProjectBase, 
    user_id: int, 
    db: Session = Depends(get_db)
):
    return crud.update_project(db, project_id, project, user_id)

@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int, 
    user_id: int, 
    db: Session = Depends(get_db)
):
    return crud.delete_project(db, project_id, user_id)


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
    return {"spec": project.environment_spec}


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
    return {"spec": project.system_spec}

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
    return {"spec": project.safety_property}


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
    return {"spec": project.config}


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

    timeout = httpx.Timeout(6000.0)  # Adjust timeout as needed (e.g., 60 seconds) # CHANGEE! STRES TESTING
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


# Reports
@app.get("/reports/{project_id}/")
async def get_reports(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project_name = f"{project.name}-{project.id}"
    
    # Make an HTTP request to the second endpoint to list project files
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PIPELINE_SERVER_ADDRESS}/service/projects/{project_name}/")
            response.raise_for_status()  # Raise an error for 4xx/5xx responses
        except httpx.HTTPStatusError as e:
            return JSONResponse(content={"error": f"Failed to retrieve files: {e}."}, status_code=500)
        except httpx.RequestError as e:
            return JSONResponse(content={"error": f"Request failed: {e}."}, status_code=500)
    
    files = response.json().get("files", [])
    
    # Filter out only PDF files
    pdf_files = [file for file in files if file.lower().endswith('.html')] #pdf
    
    # Build the URL for each PDF file
    pdf_urls = [f"{PIPELINE_SERVER_ADDRESS}/{file}" for file in pdf_files]
    
    return {"reports": pdf_urls}


@app.get("/solutions/{project_id}/")
async def get_reports(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    project_name = f"{project.name}-{project.id}"
    
    # Make an HTTP request to the second endpoint to list project files
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PIPELINE_SERVER_ADDRESS}/service/projects/solution/{project_name}/")
            response.raise_for_status()  # Raise an error for 4xx/5xx responses
        except httpx.HTTPStatusError as e:
            return JSONResponse(content={"error": f"Failed to retrieve files: {e}."}, status_code=500)
        except httpx.RequestError as e:
            return JSONResponse(content={"error": f"Request failed: {e}."}, status_code=500)
    
    files = response.json().get("files", [])
    
    # Filter out only PDF files
    aut_files = [file for file in files if file.lower().endswith('.aut')] #pdf
    
    # Build the URL for each PDF file
    aut_urls = [f"{PIPELINE_SERVER_ADDRESS}/{file}" for file in aut_files]
    
    return {"solutions": aut_urls}

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


@app.get("/service/lts-to-png")
async def generate_png_from_lts(ltlContent: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(PIPELINE_SERVER_ADDRESS + "/service/lts-to-png", params={"ltlContent": ltlContent})
            response.raise_for_status()
            return response.json()  # Assuming the target service returns JSON
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error: {str(e)}")


@app.get("/service/gemini/{project_id}/")
async def talk_to_gemini(project_id: int, solution_name: str, user_query: str, db: Session = Depends(get_db)):
    # Retrieve project information from the database
    project = crud.get_project(db, project_id)
    project_name = f"{project.name}-{project.id}"

    try:
        # Send the request to the updated gemini service endpoint
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:  # Set timeout to 120 seconds
            response = await client.get(
                PIPELINE_SERVER_ADDRESS + f"/service/gemini/{project_name}/",
                params={
                    "solution_name": solution_name,
                    "user_query": user_query
                }
            )
            response.raise_for_status()
            print(f"Received response of query {user_query}")
            return response.json()  # Assuming the target service returns JSON
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error: {str(e)}")




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

    return {"message": "System spec updated successfully in database and file"}

    #return {"message": f"{spec_filename} spec saved successfully in {project_folder}."}



# Chat
@app.post("/chat-state/")
def api_create_or_update_chat_state(chat_state: ChatStateCreate, db: Session = Depends(get_db)):
    try:
        create_or_update_chat_state(db, chat_state)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-state/{project_id}/{solution_name}", response_model=ChatStateResponse)
def api_get_chat_state(project_id: int, solution_name: str, db: Session = Depends(get_db)):
    chat_state = get_chat_state(db, project_id, solution_name)
    if not chat_state:
        raise HTTPException(status_code=404, detail="Chat state not found")
    return chat_state
