import os
import json
from datetime import datetime
from PIL import Image

def generate_output_document_html(project_folder):
    os.chdir(project_folder)
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    generate_html(f"{project_folder.split('/')[-1]}_summary_{date_time_str}.html")

def add_image_to_html(html, image_path, title):
    with Image.open(image_path) as img:
        img_width, img_height = img.size
        ratio = min(600/img_width, 400/img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
    html += f"<h2>{title}</h2>\n"
    html += f'<img src="{image_path}" width="{new_width}" height="{new_height}"><br>\n'
    return html

def add_text_annotation_html(html, text):
    html += f"<p>{text}</p>\n"
    return html

def add_json_to_html(html, json_path):
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
        formatted_json = json.dumps(json_data, indent=4)
        html += "<pre>\n"
        html += formatted_json
        html += "\n</pre>\n"
    return html

def generate_html(output_path):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Summary</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f9f9f9;
        }
        h1, h2 {
            color: #333;
        }
        p {
            line-height: 1.6;
            color: #666;
        }
        img {
            margin-bottom: 20px;
            border: 1px solid #ccc;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            border: 1px solid #ddd;
            overflow: auto;
        }
        .accordion {
            background-color: #eee;
            color: #444;
            cursor: pointer;
            padding: 10px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 15px;
            transition: 0.4s;
            margin-top: 10px;
        }
        .active, .accordion:hover {
            background-color: #ccc;
        }
        .panel {
            padding: 0 18px;
            background-color: white;
            display: none;
            overflow: hidden;
        }
    </style>
</head>
<body>
<h1>Project Summary</h1>
"""
    # Image paths
    images = [
        ("System Specification Diagram", "sys.png"),
        ("User Environment Diagram", "env.png"),
        ("Safety Property Diagram", "safety.png")
    ]
    
    # Add system, environment, and property images with annotations
    for title, img in images:
        if os.path.exists(img):
            html += f'<button class="accordion">{title}</button>'
            html += '<div class="panel">'
            html = add_image_to_html(html, img, title)
            html += '</div>'
    
    # Add configurations
    config_path = "config-pareto.json"
    if os.path.exists(config_path):
        html += '<button class="accordion">Configurations</button>'
        html += '<div class="panel">'
        html = add_json_to_html(html, config_path)
        html += '</div>'
    
    # Add solutions
    solution_files = sorted([f for f in os.listdir() if f.startswith("solution_") and f.endswith(".png")])
    for solution in solution_files:
        if os.path.exists(solution):
            title = f"Solution: {solution}"
            html += f'<button class="accordion">{title}</button>'
            html += '<div class="panel">'
            html = add_image_to_html(html, solution, title)
            html += '</div>'
    
    html += """
<script>
    var acc = document.getElementsByClassName("accordion");
    var i;
    for (i = 0; i < acc.length; i++) {
        acc[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var panel = this.nextElementSibling;
            if (panel.style.display === "block") {
                panel.style.display = "none";
            } else {
                panel.style.display = "block";
            }
        });
    }
</script>
</body>
</html>
"""
    with open(output_path, "w") as file:
        file.write(html)
    print(f"HTML report saved as {output_path}")

# Example usage
generate_output_document_html("projects/EVoting")
