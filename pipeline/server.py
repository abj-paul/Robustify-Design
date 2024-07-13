import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload/files")
async def upload_files(files: List[UploadFile] = File(...), project_folder: str = Form(...)):
    file_details = []
    for file in files:
        file_location = os.path.join(project_folder, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        file_details.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": os.path.getsize(file_location)
        })
    return file_details


@app.post("/upload/specification/")
async def upload_specification(filename: str = Form(...), specification: str = Form(...), project_folder: str = Form(...)):
    file_location = os.path.join(project_folder, filename)
    with open(file_location, "w") as f:
        f.write(specification)

    return {"filename": filename, "size": os.path.getsize(file_location)}


@app.post("/create_project/")
async def create_project(
    project_name: str = Form(...),
    project_description: str = Form(...),
    project_image: UploadFile = File(...),
):
    try:
        # Create a folder with project name if it doesn't exist
        project_folder = f"./projects/{project_name}"
        os.makedirs(project_folder, exist_ok=True)

        # Save project description to a file
        description_file = os.path.join(project_folder, "description.txt")
        with open(description_file, "w") as f:
            f.write(project_description)
        # Save project image
        image_path = os.path.join(project_folder, project_image.filename)
        with open(image_path, "wb") as f:
            f.write(project_image.file.read())
        print("Control reach here")

        return {"message": "Project created successfully", "project_name": project_name, "project_folder": project_folder}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


# Run the application with the command:
# uvicorn main:app --reload
