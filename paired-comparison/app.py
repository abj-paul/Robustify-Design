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

def load_existing_pairs():
    """Load all existing pairs from the CSV file to avoid duplicates."""
    existing_pairs = set()
    try:
        with open(CSV_FILE, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    # Assuming the first two columns are image1 and image2
                    image1, image2 = row[0], row[1]
                    # Store pairs in a way that (image1, image2) == (image2, image1)
                    existing_pairs.add(tuple(sorted([image1, image2])))
    except FileNotFoundError:
        # If the CSV file doesn't exist, no pairs have been compared yet
        pass
    print(f"Processed {len(existing_pairs)} samples so far.")
    return existing_pairs

@app.get("/random-images")
async def get_random_images():
    """API to get two random images for comparison, ensuring no duplicate pairs."""
    images = [img for img in os.listdir(IMAGE_DIR) if img.endswith((".png", ".jpg", ".jpeg"))]
    if len(images) < 2:
        return JSONResponse(content={"error": "Not enough images found"}, status_code=404)
    
    existing_pairs = load_existing_pairs()

    # Randomly sample until a new pair is found or reach a limit
    max_attempts = 100  # Limit the number of attempts to avoid an infinite loop if almost all pairs are in the CSV
    for attempt in range(max_attempts):
        image1, image2 = random.sample(images, 2)
        pair = tuple(sorted([image1, image2]))

        # If this pair is new, proceed
        if pair not in existing_pairs:
            # Track a serial number based on the CSV length
            serial_number = len(existing_pairs) + 1  # Incremental serial number based on unique pairs in the CSV
            return {
                "serial_number": serial_number,
                "image1": f"/images/{image1}",
                "image2": f"/images/{image2}"
            }
    
    return JSONResponse(content={"error": "No new pairs available"}, status_code=404)

@app.post("/submit")
async def submit_annotation(data: AnnotationData):
    """API to submit annotation"""
    print(f"Selected Image: {data.selected}, Time taken to decide: {data.time_taken}")
    print(f"Image                                                           | Time needed |")
    print(f"{data.image1} | {data.focus_time_image1}")
    print(f"{data.image2} | {data.focus_time_image2}")

    with open(CSV_FILE, mode="a", newline="") as file:
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
