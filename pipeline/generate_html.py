import os
import json
from datetime import datetime
from PIL import Image
from libs.design_ranking import rank_designs

def generate_output_document_html(project_folder):
    os.chdir(project_folder)
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    generate_html(project_folder,f"{project_folder.split('/')[-1]}_summary_{date_time_str}.html")
    os.chdir("../..")


def add_image_to_html(html, image_path, project_folder, title):
    with Image.open(image_path) as img:
        img_width, img_height = img.size
        ratio = min(600/img_width, 400/img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
    html += f"<h2>{title}</h2>\n"
    html += f'<img src="http://localhost:8000/{project_folder}/{image_path}" width="{new_width}" height="{new_height}"><br>\n'
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

def generate_html(project_folder, output_path):
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

    html += """
<button id="expandAll" style="margin-bottom: 20px;">Expand All</button>
<script>
    var acc = document.getElementsByClassName("accordion");
    var i;

    // Expand All button logic
    document.getElementById("expandAll").addEventListener("click", function() {
        var allPanelsOpen = Array.from(acc).every(accItem => accItem.classList.contains("active"));
        for (i = 0; i < acc.length; i++) {
            if (!allPanelsOpen) {
                acc[i].classList.add("active");
                acc[i].nextElementSibling.style.display = "block";
            } else {
                acc[i].classList.remove("active");
                acc[i].nextElementSibling.style.display = "none";
            }
        }
        this.textContent = allPanelsOpen ? "Expand All" : "Collapse All";
    });

    // Individual accordion toggle logic
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
            html = add_image_to_html(html, f"{img}", project_folder, title)
            html += '</div>'
    
    # Add configurations
    config_path = "config-pareto.json"
    if os.path.exists(config_path):
        html += '<button class="accordion">Configurations</button>'
        html += '<div class="panel">'
        html = add_json_to_html(html, config_path)
        html += '</div>'
    
    # Add solutions
    os.chdir("../..")
    ranked_designs = rank_designs(project_folder)
    os.chdir(project_folder)

    for index,design in enumerate(ranked_designs):
        print(f"Ranking now {design['solution']}")
        solution_path = design['solution']
        title = f"Solution: {os.path.basename(solution_path)}"
        
        # Add the accordion button for the solution
        html += f'<button class="accordion">{title}</button>'
        html += '<div class="panel">'
        
        # Add solution image
        print(solution_path.replace('.aut', '.png').replace("solutions/","").replace("sol","solution_"))
        html = add_image_to_html(html, solution_path.replace('.aut', '.png').replace("sol","solution_"), project_folder, title)
        
        # Add ranking data
        #html += f'<p><strong>Complexity:</strong> {design["_complexity"]}</p>'
        html += f'<p><strong>Albin Complexity:</strong> {design["albin_complexity"]}</p>'
        html += f'<p><strong>Girvan-Newman Modularity:</strong> {design["girvan_newman_modularity"]}</p>'
        html += f'<p><strong>Jaccard Redundancy:</strong> {design["jaccard_redundancy"]}</p>'
        html += f'<p><strong>Laplacian Spectral Complexity:</strong> {design["laplacian_spectral_complexity"]}</p>'
        html += f'<p><strong>Eigen Symmetry:</strong> {design["eigen_symmetry"]}</p>'
        html += f'<a href="http://localhost:8000/projects/Voting-2/solution_{index+1}.xml" target="_blank">Download Design </a> <br>'
        # Close the panel for the current design
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

    print(os.curdir)
    with open(output_path, "w") as file:
        file.write(html)
    print(f"HTML report saved as {output_path}")

# Example usage
#generate_output_document_html("projects/EVoting")
