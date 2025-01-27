from dotenv import load_dotenv
import os
import google.generativeai as genai
import numpy as np

# Load environment variables
load_dotenv()

FUNDAMENTAL_PROMPT = '''
Fortis is a system that takes the behavioral model of a system and robustifies it against environmental deviations to satisfy the safety property. The systems are mostly cyber-physical in nature. So the generated redesigns may be interpreted as hardware, software, sensor etc changes. Cost is also a concern. Note that, the user does not want to know code implementation, rather how the design can be implemented from a high level view - changes can be in hardware, software, sensor, interaction etc.
'''

def get_response_from_gemini(sys, env, p, redesign, system_description, user_query):
    # Configure the API
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Convert numpy data types to native Python types for JSON serialization
    def serialize_data(data):
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, (np.int64, np.float64)):
            return data.item()
        elif isinstance(data, dict):
            return {k: serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [serialize_data(item) for item in data]
        else:
            return data

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

    # Prepare the query as a single string
    prompt = f"""
**Role**: You are a behavioral system design analyzer. Your task is to help user in design comprehension task. User explores the designs to understand how the generated robust wokrs with respect to original system behavioral design.

**Context**:
- System Behavioral Design: {sys}
- Environment Model: {env}
- Safety Property: {p}
- Generated Robust Design (using Fortis): {redesign}
- System Description: {system_description}

**Fundamental Principles**:
{FUNDAMENTAL_PROMPT}

**User Query**: {user_query}
"""
    print(prompt)
    # Get response
    response = model.generate_content([prompt])  # Ensure the query is passed as a list
    return response.text  # Return only the text of the response

