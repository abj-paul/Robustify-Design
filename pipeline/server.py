import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
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

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/files")
async def upload_files(files: List[UploadFile] = File(...)):
    file_details = []
    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        file_details.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": os.path.getsize(file_location)
        })
    return file_details


@app.post("/upload/specification/")
async def upload_specification(filename: str = Form(...), specification: str = Form(...)):
    file_location = os.path.join(UPLOAD_DIR, filename)
    with open(file_location, "w") as f:
        f.write(specification)

    return {"filename": filename, "size": os.path.getsize(file_location)}

# Run the application with the command:
# uvicorn main:app --reload
