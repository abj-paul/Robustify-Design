import numpy as np
import os
import networkx as nx
from networkx.algorithms.community import girvan_newman  
import numpy as np
from scipy.sparse import csr_matrix
from scipy.linalg import eigvals
from sklearn.metrics import jaccard_score


def get_matrices_from_aut_file(filename):
    with open(filename, 'r') as file:
        content = file.read()

    edges = []
    for line in content.strip().split('\n')[1:]:  # Skipping the 'des' line
        parts = line.strip('()').split(', ')
        start, event, end = int(parts[0]), parts[1].strip('"'), int(parts[2])
        edges.append((start, event, end))

    # Extract unique nodes
    nodes = set()
    for edge in edges:
        nodes.add(edge[0])
        nodes.add(edge[2])

    # Create node index mapping
    node_index = {node: idx for idx, node in enumerate(sorted(nodes))}

    # Initialize an adjacency matrix
    size = len(node_index)
    matrix_numeric = np.zeros((size, size), dtype=int)
    matrix_labeled = np.full((size, size), None, dtype=object)

    # Populate the adjacency matrix with event names
    for start, event, end in edges:
        start_idx = node_index[start]
        end_idx = node_index[end]
        matrix_labeled[start_idx][end_idx] = event  # Store the event name

    # Populate the adjacency matrix
    for start, event, end in edges:
        start_idx = node_index[start]
        end_idx = node_index[end]
        matrix_numeric[start_idx][end_idx] = 1  # Edge from start to end
    return matrix_numeric, matrix_labeled

    

# Calculate Albin Complexity
def albin_complexity(adj_matrix):
    # Convert adjacency matrix to a directed graph
    G = nx.DiGraph(adj_matrix)

    # Number of nodes (order of the graph)
    n = len(G.nodes)

    # Sum of degrees for each node
    degree_sum = sum(dict(G.degree()).values())

    # Longest path length in the graph
    try:
        longest_path = nx.dag_longest_path_length(G)
    except nx.NetworkXUnfeasible:
        # Handle case if the graph has cycles (not a DAG)
        longest_path = 0

    # Calculate Albin Complexity
    albin_complexity_value = n + degree_sum + longest_path
    return albin_complexity_value




def girvan_newman_modularity(adj_matrix):
    graph = nx.from_numpy_array(adj_matrix, create_using=nx.Graph())

    # Use Girvan-Newman to find communities
    communities = list(girvan_newman(graph))  # Updated function call

    max_modularity = -np.inf  # Initialize to a very low value to track the maximum modularity
    best_num_communities = 0  # Initialize to track the number of communities for max modularity

    # Iterate over levels of community division (2, 3, 4 communities)
    for level in range(2, 5):  # Checking for 2, 3, and 4 communities
        if len(communities) < level:  # If there are fewer communities than the level, skip
            continue

        # Select the level with the desired number of communities
        selected_communities = communities[level - 1]  # Level 1 gives 2 communities, etc.

        # Assign community labels to nodes (node indices)
        num_states = adj_matrix.shape[0]  # Number of nodes (rows/columns of the matrix)
        community_labels = np.zeros(num_states, dtype=int)

        # Assign labels for each community
        for idx, community in enumerate(selected_communities):
            for node in community:
                community_labels[node] = idx

        # Total number of edges (since it's an undirected graph, count once)
        total_edges = adj_matrix.sum() / 2  # Each edge is counted twice in an undirected graph

        # Compute modularity based on adjacency matrix and community labels
        Q = 0.0
        branching_factors = np.sum(adj_matrix, axis=1)  # Degree (or branching factor) for each node

        for i in range(num_states):
            for j in range(num_states):
                if community_labels[i] == community_labels[j]:  # nodes in the same community
                    A_ij = adj_matrix[i, j]  # adjacency matrix entry
                    Q += A_ij - (branching_factors[i] * branching_factors[j]) / (2 * total_edges)

        Q /= (2 * total_edges)

        # Track the maximum modularity and associated labels and number of communities
        if Q > max_modularity:
            max_modularity = Q
            best_community_labels = community_labels
            best_num_communities = len(selected_communities)

    return max_modularity



# Redundancy Detection using Jaccard Index
def calculate_redundancy_jaccard(adj_matrix):
    num_states = adj_matrix.shape[0]
    total_jaccard_sum = 0
    num_comparisons = 0

    for i in range(num_states):
        for j in range(i + 1, num_states):
            # Get outgoing transitions for states i and j
            outgoing_i = adj_matrix[i].flatten()  # No need for toarray() if adj_matrix is already ndarray
            outgoing_j = adj_matrix[j].flatten()  # Same here for outgoing_j

            # Calculate Jaccard index
            jaccard_index = jaccard_score(outgoing_i, outgoing_j)
            total_jaccard_sum += jaccard_index
            num_comparisons += 1

    # Calculate average Jaccard index for redundancy
    average_jaccard_index = total_jaccard_sum / num_comparisons if num_comparisons > 0 else 0
    return average_jaccard_index



def calculate_symmetry_eigenvalues(adj_matrix):
    # Compute eigenvalues of the adjacency matrix
    eigenvalues = eigvals(adj_matrix.toarray())

    # Count repeated eigenvalues to estimate symmetry
    unique, counts = np.unique(np.round(eigenvalues, decimals=5), return_counts=True)
    repeated_eigenvalues = dict(zip(unique, counts))

    # The number of repeated eigenvalues provides an indication of symmetry
    symmetry_measure = sum(count > 1 for count in counts)  # Count repeated eigenvalues

    return repeated_eigenvalues, symmetry_measure


# Define the functions to compute Laplacian, spectral norm, and complexity
def compute_laplacian_matrix(adjacency_matrix):
    """Compute the Laplacian matrix from the adjacency matrix."""
    degree_matrix = np.diag(np.sum(adjacency_matrix, axis=1))
    laplacian_matrix = degree_matrix - adjacency_matrix
    return laplacian_matrix

def compute_spectral_norm(laplacian_matrix):
    """Compute the spectral norm (Euclidean norm) of the eigenvalues of the Laplacian matrix."""
    eigenvalues = np.linalg.eigvalsh(laplacian_matrix)  # Compute eigenvalues
    spectral_norm = np.linalg.norm(eigenvalues)         # Compute Euclidean norm
    return spectral_norm

def compute_laplacian_spectral_complexity(adjacency_matrix):
    """
    Calculate the complexity of a graph using the spectral norm of the Laplacian
    matrix and its complement.
    """
    # Step 1: Compute Laplacian and spectral norm for the original graph
    laplacian_matrix = compute_laplacian_matrix(adjacency_matrix)
    spectral_norm_original = compute_spectral_norm(laplacian_matrix)

    # Step 2: Compute Laplacian and spectral norm for the complement graph
    n = adjacency_matrix.shape[0]
    complement_adjacency = np.ones((n, n)) - adjacency_matrix - np.eye(n)  # Complement adjacency matrix
    laplacian_complement = compute_laplacian_matrix(complement_adjacency)
    spectral_norm_complement = compute_spectral_norm(laplacian_complement)

    # Step 3: Complexity measure is the product of the norms
    complexity_measure = spectral_norm_original * spectral_norm_complement
    return complexity_measure


# Pareto optimality check
def pareto_optimal(evaluations, metrics):
    pareto_front = []
    last_part = []
    for solution_a in evaluations:
        is_dominated = False
        for solution_b in evaluations:
            if solution_a == solution_b:
                continue  # Skip comparing a solution to itself
            # Check if solution_b dominates solution_a
            if all(solution_b[metric] >= solution_a[metric] for metric in metrics):
                is_dominated = True
                break
        if not is_dominated:
            pareto_front.append(solution_a)
        else :
            last_part.append(solution_a)
    return pareto_front + last_part

#Ranking function for Pareto optimal solutions
def rank_solutions(evaluations, metrics):
    # Step 1: Find Pareto optimal solutions
    pareto_front = pareto_optimal(evaluations, metrics)
    
    # Step 2: Rank Pareto optimal solutions based on a selected metric, e.g., albin_complexity
    ranked_solutions = sorted(pareto_front, key=lambda x: x['albin_complexity'], reverse=False)
    
    return ranked_solutions


def rank_designs(project_directory):
    generated_design_evaluations = []
    for file in os.listdir(f"{project_directory}/solutions"):
        if file.endswith(".aut"):
            filepath = os.path.join(f"{project_directory}/solutions", file)
            temp = get_matrices_from_aut_file(filepath)
            
            sparse_adj_matrix = csr_matrix(temp[0])

            generated_design_evaluations.append({
                "solution": file,
                "numeric": temp[0],
                "labeled": temp[1],
                "albin_complexity": albin_complexity(temp[0]),
                "girvan_newman_modularity": girvan_newman_modularity(temp[0]),
                "jaccard_redundancy": calculate_redundancy_jaccard(temp[0]),
                "eigen_symmetry": calculate_symmetry_eigenvalues(sparse_adj_matrix)[1],
                "state_length": len(temp[0]),
                "laplacian_spectral_complexity": compute_laplacian_spectral_complexity(temp[0]),
                "gpt_comments": "GPT Comments on design"
            })
    print(f"During ranking, there are {len(generated_design_evaluations)} designs.")

    metrics = ["albin_complexity", "girvan_newman_modularity", "jaccard_redundancy", "eigen_symmetry", "state_length", "laplacian_spectral_complexity"]
    ranked_designs = rank_solutions(generated_design_evaluations, metrics)
    
    return ranked_designs


# for rank, design in enumerate(rank_designs("../projects/Voting-2")):
#     print(f"Rank {rank}: {design['solution']} - Albin Complexity: {design['albin_complexity']}")

#print(rank_designs("../projects/Voting-2"))