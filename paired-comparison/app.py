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
ANNOTATION_FILE1 = "annotations.csv"     # Primary annotation file
ANNOTATION_FILE2 = "annotations2.csv"    # Second annotator’s file

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
if not os.path.exists(ANNOTATION_FILE2):
    with open(ANNOTATION_FILE2, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Image1", "Image2", "Selected", "Timestamp"])


def load_pairs_from_file(file_path: str) -> list[tuple[str, str]]:
    """Load image pairs from a specified annotation file."""
    pairs = []
    try:
        with open(file_path, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pairs.append((row["image1"], row["image2"]))
    except FileNotFoundError:
        pass  # If the file doesn't exist, return an empty list
    return pairs

@app.get("/random-images")
async def get_random_images():
    """Retrieve the next unannotated image pair for the second annotator."""
    # Load image pairs from both annotation files
    existing_pairs_annotator1 = load_pairs_from_file(ANNOTATION_FILE1)
    existing_pairs_annotator2 = load_pairs_from_file(ANNOTATION_FILE2)

    # Determine the index based on the number of annotations by the second annotator
    index = len(existing_pairs_annotator2)

    # Check if the index is within bounds of the first annotator's file
    if index >= len(existing_pairs_annotator1):
        return JSONResponse(content={"error": "No new pairs available"}, status_code=404)

    # Retrieve the image pair at the specified index
    image1, image2 = existing_pairs_annotator1[index]
    serial_number = index + 1  # Serial number for reference

    return {
        "serial_number": serial_number,
        "image1": f"/images/{image1}",
        "image2": f"/images/{image2}"
    }


@app.post("/submit")
async def submit_annotation(data: AnnotationData):
    """API to submit annotation"""
    print(f"Selected Image: {data.selected}, Time taken to decide: {data.time_taken}")
    print(f"Image                                                           | Time needed |")
    print(f"{data.image1} | {data.focus_time_image1}")
    print(f"{data.image2} | {data.focus_time_image2}")

    with open(ANNOTATION_FILE2, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data.image1, data.image2, data.selected, data.focus_time_image1, data.focus_time_image2, data.time_taken])
    return JSONResponse(content={"message": "Annotation saved successfully!"})

@app.get("/images/{image_name}")
async def serve_image(image_name: str):
    """Serve an image file from the IMAGE_DIR"""
    image_path = os.path.join(IMAGE_DIR, image_name)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return JSONResponse(content={"error": "Image not found"}, status_code=404)
