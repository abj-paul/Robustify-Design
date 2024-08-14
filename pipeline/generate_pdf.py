from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import os
import json
from datetime import datetime

def generate_output_document(project_folder):
    os.chdir(project_folder)
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    generate_pdf(f"{project_folder.split('/')[-1]}_summary_{date_time_str}.pdf")
    os.chdir("../..")

def add_image_to_canvas(c, image_path, x, y, max_width, max_height):
    with Image.open(image_path) as img:
        img_width, img_height = img.size
        ratio = min(max_width/img_width, max_height/img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio
        c.drawImage(ImageReader(img), x, y, width=new_width, height=new_height)

def add_text_annotation(c, text, x, y, max_width):
    c.setFont("Helvetica", 12)
    lines = text.split('\n')
    for line in lines:
        c.drawString(x, y, line)
        y -= 14  # Move to the next line
    return y

def add_json_to_canvas(c, json_path, x, y, max_width):
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
        formatted_json = json.dumps(json_data, indent=4)
        lines = formatted_json.split('\n')
        for line in lines:
            if y < 50:  # Start a new page if there's no more room
                c.showPage()
                c.setFont("Helvetica", 12)
                y = letter[1] - 30
            c.drawString(x, y, line)
            y -= 14  # Move to the next line
    return y

def generate_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Image paths
    images = [
        ("System Specification Diagram", "sys.png"),
        ("User Environment Diagram", "env.png"),
        ("Safety Property Diagram", "safety.png")
    ]
    
    # Add system, environment, and property images with annotations
    for title, img in images:
        if os.path.exists(img):
            y = height - 30
            y = add_text_annotation(c, title, 30, y, width - 60)
            add_image_to_canvas(c, img, 30, y - 270, width - 60, 250)
            c.showPage()
    
    # Add configurations
    config_path = "config-pareto.json"
    if os.path.exists(config_path):
        y = height - 30
        y = add_text_annotation(c, "Configurations:", 30, y, width - 60)
        y = add_json_to_canvas(c, config_path, 30, y - 14, width - 60)
        c.showPage()
    
    # Add solutions
    solution_files = sorted([f for f in os.listdir() if f.startswith("solution_") and f.endswith(".png")])
    for solution in solution_files:
        if os.path.exists(solution):
            y = height - 30
            title = f"Solution: {solution}"
            y = add_text_annotation(c, title, 30, y, width - 60)
            add_image_to_canvas(c, solution, 30, y - 270, width - 60, 250)
            c.showPage()
    
    c.save()

