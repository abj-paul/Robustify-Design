import os
import numpy as np
import joblib

# Function to load a single .aut file and return its adjacency matrix
def load_aut_file(file_path):
    edges = []
    nodes = set()
    
    with open(file_path, 'r') as file:
        for line in file:
            # Skip lines that don't contain graph data (e.g., lines with 'des' or other non-graph data)
            if line.startswith("des") or not line.strip():
                continue

            parts = line.strip().strip('()').split(',')
            if len(parts) == 3:
                try:
                    source = int(parts[0].strip())
                    action = parts[1].strip()  # Action (ignored in the adjacency matrix)
                    destination = int(parts[2].strip())

                    edges.append((source, destination))
                    nodes.add(source)
                    nodes.add(destination)
                except ValueError:
                    # Skip lines that do not conform to the expected format
                    print(f"Skipping invalid line: {line.strip()}")
                    continue
    
    nodes = sorted(nodes)
    node_index = {node: idx for idx, node in enumerate(nodes)}
    
    matrix_size = len(nodes)
    adj_matrix = np.zeros((matrix_size, matrix_size), dtype=int)
    
    for source, destination in edges:
        source_idx = node_index[source]
        destination_idx = node_index[destination]
        adj_matrix[source_idx, destination_idx] = 1  # Binary edges (unweighted)
    
    return adj_matrix, nodes

# Load all .aut files and build adjacency matrices for each one
def load_all_aut_files(base_dir):
    aut_matrices = {}
    
    print(f"Looking for .aut files in directory: {base_dir}")
    
    if os.path.isdir(base_dir):
        print(f"Found directory: {base_dir}")
        for file_name in os.listdir(base_dir):
            if file_name.endswith('.aut'):
                file_path = os.path.join(base_dir, file_name)
                
                print(f"Loading file: {file_path}")
                adj_matrix, nodes = load_aut_file(file_path)
                
                # The image_name will be based on the folder structure
                image_name = file_name.replace('.aut', '.png')
                
                aut_matrices[image_name] = adj_matrix
                # Debug: Output the matrix shape and nodes (optional)
                print(f"Loaded {file_name}: Matrix Shape = {adj_matrix.shape}")
                    
    return aut_matrices

# Save the results to a .pkl file using joblib
def save_results(aut_matrices, output_file):
    joblib.dump(aut_matrices, output_file)
    print(f"Results saved to {output_file}")

# Example usage:
base_dir = '/home/abhijit/Robustify-Design/algorithmic-design-ranking/autbucket/'  # Ensure this is the correct path to your autbucket directory
aut_matrices = load_all_aut_files(base_dir)

# Save the matrices to a joblib file
output_file = 'aut_matrices.pkl'
save_results(aut_matrices, output_file)
