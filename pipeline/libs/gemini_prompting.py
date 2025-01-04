from dotenv import load_dotenv
from design_ranking import rank_designs
import os
import google.generativeai as genai
import json
import numpy as np

# Load environment variables
load_dotenv()


def get_response_from_gemini(design_data, sys, env, p, redesign):
    # Configure the API
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Convert numpy data types to native Python types for JSON serialization
    def serialize_data(data):
        if isinstance(data, np.ndarray):
            return data.tolist()  # Convert numpy arrays to Python lists
        elif isinstance(data, (np.int64, np.float64)):  
            return data.item()  # Convert numpy scalar types to Python native types
        elif isinstance(data, dict):
            return {k: serialize_data(v) for k, v in data.items()}  # Recursively process dictionaries
        elif isinstance(data, list):
            return [serialize_data(item) for item in data]  # Recursively process lists
        else:
            return data  # Return other types as is

    design_data_serialized = serialize_data(design_data)

    # Create the model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
    )

    # Prepare the query
    query = (
        "You are a behavioral system design analyzer. Given a design, you will return "
        "insights on that design, highlighting changes and any significant observations.\n\n"
        f"Here is the design data: System behavioral model is {sys}, Environment model is {env} and safety property is {p}. Here is the generated design using Fortis tool to robustify the system. The robust design is : {redesign}. Some metrics of this robust design is: {json.dumps(design_data_serialized, indent=2)}\n\n"
        "Please provide your analysis."
    )

    # Get response
    response = model.generate_content([query])
    return response.text  # Return only the text of the response

# # Example usage
# if __name__ == "__main__":
#     example_design = {
#         "solution": "solution_file_path.aut",
#         "numeric": np.array([[1, 0], [0, 1]], dtype=np.int64),  # Example numpy array
#         "labeled": np.array(["State A", "State B"], dtype=object),  # Example numpy array
#         "albin_complexity": 3.5,
#         "girvan_newman_modularity": 0.75,
#         "jaccard_redundancy": 0.15,
#         "eigen_symmetry": 0.9,
#         "state_length": 2,
#         "laplacian_spectral_complexity": 1.25,
#         "gpt_comments": "GPT Comments on design"
#     }

#     response = get_response_from_gemini(example_design)
#     print(response)




# Get ranked designs
project_folder = "../projects/Voting-2"
ranked_designs = rank_designs(project_folder)

# Process each design
for design in ranked_designs:
    f = open(f"{project_folder}/sys.lts")
    sys = f.read()
    f.close()

    f = open(f"{project_folder}/env.lts")
    env = f.read()
    f.close()

    f = open(f"{project_folder}/p.lts")
    p = f.read()
    f.close()

    f = open(f"{project_folder}/solutions/{design['solution']}")
    redesign = f.read()
    f.close()

    response = get_response_from_gemini(design, sys, env, p, redesign)
    print(response)
    break  # Process only the first design for demonstration
