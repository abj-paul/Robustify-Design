from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import csv
import random
from datetime import datetime

app = FastAPI()

# Directory containing images
IMAGE_DIR = "./public/images"
CSV_FILE = "annotations.csv"

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, can be set to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class AnnotationData(BaseModel):
    image1: str
    image2: str
    selected: str
    time_taken: float  # Time taken for annotation in seconds
    focus_time_image1: float  # Accumulated focus time for image 1
    focus_time_image2: float  # Accumulated focus time for image 2


# Ensure CSV file exists and has headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Image1", "Image2", "Selected", "Timestamp"])

@app.get("/random-images")
async def get_random_images():
    """API to get two random images for comparison"""
    images = [img for img in os.listdir(IMAGE_DIR) if img.endswith((".png", ".jpg", ".jpeg"))]
    if len(images) < 2:
        return JSONResponse(content={"error": "Not enough images found"}, status_code=404)
    image1, image2 = random.sample(images, 2)
    return {"image1": f"/images/{image1}", "image2": f"/images/{image2}"}

@app.post("/submit")
async def submit_annotation(data: AnnotationData):
    """API to submit annotation"""
    print(f"Selected Image: {data.selected}, Time taken to decide: {data.time_taken}")
    print(f"Image                                                           | Time needed |")
    print(f"{data.image1} | {data.focus_time_image1}")
    print(f"{data.image2} | {data.focus_time_image2}")

    timestamp = datetime.now().isoformat()
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data.image1, data.image2, data.selected, data.focus_time_image1, data.focus_time_image2, timestamp])
    return JSONResponse(content={"message": "Annotation saved successfully!"})

@app.get("/images/{image_name}")
async def serve_image(image_name: str):
    """Serve an image file from the IMAGE_DIR"""
    image_path = os.path.join(IMAGE_DIR, image_name)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return JSONResponse(content={"error": "Image not found"}, status_code=404)
