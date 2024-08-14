import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from libs.parse_uml_to_lts import uml_to_lts, write_in_file
from libs.set_config import set_config
from libs.execute_fortis import run_fortis
from libs.output_to_uml import save_output_as_uml
from libs.convert_xml_to_image import convert_xml_to_image
from wrapper import convert_to_lts
from generate_pdf import generate_output_document
from generate_html import generate_output_document_html

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

@app.post("/configuration")
async def upload_configuration(
    configuration: str = Form(...),
    project_folder: str = Form(...)
):
    try:
        file_location = os.path.join(project_folder, "config-pareto.json")
        with open(file_location, "w") as f:
            f.write(configuration)

        return {"status": "Configuration Saved"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@app.post("/execute")
async def upload_additional( project_folder: str = Form(...), class_list: List[str] = Form(...)): # class_list = ["barcode-reader.xml","booking-program.xml","printer.xml"]
    if len(class_list[0])!=0: 
        convert_to_lts(project_folder, class_list, not os.path.isfile(f"{project_folder}/env.xml"))
        for class_name in class_list:
            convert_xml_to_image(project_folder,class_name)
        
    else:
        try:
            write_in_file(f"{project_folder}/sys.lts", uml_to_lts(f"{project_folder}/sys.xml"), "System LTS Model")
            write_in_file(f"{project_folder}/env.lts", uml_to_lts(f"{project_folder}/env.xml"), "Environment LTS Model")
        except:
            print("Found no file and stuffs")
    run_fortis(project_folder)

    save_output_as_uml(project_folder)

    solution_index = 1
    for filename in os.listdir(f"{project_folder}/solutions/"):
        if filename.endswith(".aut"):
            convert_xml_to_image(f"{project_folder}",f"solution_{solution_index}.xml")
            solution_index+=1

    convert_xml_to_image(project_folder,"sys.xml")
    convert_xml_to_image(project_folder,"env.xml")
    generate_output_document(project_folder)
    generate_output_document_html(project_folder)

    return {"status": f"Fortis executed. Report in {os.getcwd()}"}



@app.get("/get-file-content/")
async def get_file_content(file_path: str):
    now = datetime.now()
    time_format = "%I:%M %p"  # 12-hour format with AM/PM
    formatted_time = now.strftime(time_format)
    print(f"Recieved request at {formatted_time}")
    if os.path.exists(file_path) and os.path.isfile(file_path):
        print(f"Serving request at {formatted_time}")
        return FileResponse(file_path)
    else:
        print(f"Failed to process request at {formatted_time}")
        raise HTTPException(status_code=404, detail="File not found")



# Run the application with the command:
# uvicorn main:app --reload
