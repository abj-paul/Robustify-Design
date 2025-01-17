# -*- coding: utf-8 -*-
"""EDA of Paired Comparison Annotation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rPDott7-k_pof3tin_KauTB29v1GH7vv
"""

from google.colab import drive
drive.mount("/content/drive")

address = "annotations - annotations.csv"
!ls "{address}" -alh

import pandas as pd
df = pd.read_csv(address)
df

df.columns

"""### Active Ranking using Pairwise Comparisons

"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
# Step 2: Prepare the data (image pairs and outcomes)
# We assume the 'selected' column has 1 if image1 was selected and 0 if image2 was selected
# Create a new column for the outcome: 1 if image1 is selected, 0 if image2 is selected
df['outcome'] = (df['selected'] == df['image1']).astype(int)

# Count the frequency of each image pair comparison
pair_counts = df.groupby(['image1', 'image2']).size().reset_index(name='count')

# Initialize the item strengths (parameters) for each image (starting with 0 for all images)
unique_images = pd.concat([pair_counts['image1'], pair_counts['image2']]).unique()
strengths = {img: 0.0 for img in unique_images}  # Initial guess: all images have strength 0

# Step 3: Define the negative log-likelihood function
def negative_log_likelihood(strengths, pair_counts, df):
    log_likelihood = 0
    strength_dict = {img: strength for img, strength in zip(df['image1'].unique(), strengths)}

    for _, row in pair_counts.iterrows():
        image1, image2, count = row['image1'], row['image2'], row['count']

        # Compute the probability of image1 winning based on strengths
        prob = 1 / (1 + np.exp(strength_dict[image2] - strength_dict[image1]))

        # Find the outcome from the original dataset
        outcome = df[(df['image1'] == image1) & (df['image2'] == image2)]['outcome'].iloc[0]

        # Log-likelihood for the current pair
        if outcome == 1:
            log_likelihood += count * np.log(prob)
        else:
            log_likelihood += count * np.log(1 - prob)

    return -log_likelihood  # Return negative log-likelihood for minimization

# Step 4: Optimize the likelihood function to estimate the strengths of the images
# We need to pass the current strengths and data to the optimization function
initial_strengths = np.array([strengths[img] for img in unique_images])  # Initial strengths for each image

# Optimize using the BFGS method
result = minimize(negative_log_likelihood, initial_strengths, args=(pair_counts, df), method="BFGS")

# The optimized strengths (parameters) for each image
optimized_strengths = result.x

# Create a dictionary mapping each image to its estimated strength
strength_dict = {img: strength for img, strength in zip(unique_images, optimized_strengths)}

# Step 5: Rank the images based on their estimated strengths
ranked_images = sorted(strength_dict.items(), key=lambda x: x[1], reverse=True)

# Step 6: Output the ranked list of images
print("Ranked Images (from most to least preferred):")
for rank, (image, strength) in enumerate(ranked_images, 1):
    print(f"{rank}. {image} (Strength: {strength})")

import numpy as np
import pandas as pd
import random
from scipy.spatial.distance import cdist


# Prepare the pairwise comparison data
matches = []
for _, row in df.iterrows():
    image1 = row['image1']
    image2 = row['image2']
    selected = row['selected']

    if selected == image1:
        matches.append((image1, image2, 1))  # image1 wins
        matches.append((image2, image1, 0))  # image2 loses
    else:
        matches.append((image2, image1, 1))  # image2 wins
        matches.append((image1, image2, 0))  # image1 loses

# Matches are now a list of tuples with (winner, loser, outcome)
matches_df = pd.DataFrame(matches, columns=['team1', 'team2', 'win'])

# Step 2: Initialize Ranking and Utility of Items
# Let's assume we start with a random ranking of the images
items = list(set(matches_df['team1']).union(set(matches_df['team2'])))
n_items = len(items)
initial_ranking = {item: random.uniform(0, 1) for item in items}

# Function to compute acquisition (uncertainty) based on current ranking
def acquisition_function(ranking, item1, item2):
    # For simplicity, we use a random approach for now
    # In the paper, they use a more sophisticated acquisition strategy
    return abs(ranking[item1] - ranking[item2])

# Step 3: Active Ranking Process (Iterative Comparison Selection)
def active_ranking(matches, ranking, n_comparisons=50):
    # Initialize results
    rankings_history = []

    for _ in range(n_comparisons):
        # Select the next pair of items to compare based on uncertainty
        min_acq = float('inf')
        selected_pair = None

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                item1, item2 = items[i], items[j]
                acq_value = acquisition_function(ranking, item1, item2)

                if acq_value < min_acq:
                    min_acq = acq_value
                    selected_pair = (item1, item2)

        # Simulate a comparison between the selected pair (this would be from your CSV data in reality)
        item1, item2 = selected_pair
        comparison_result = random.choice([0, 1])  # Randomly choose winner for simplicity

        # Update the ranking based on the result of the comparison
        if comparison_result == 1:
            ranking[item1] += 0.1  # Image1 wins
            ranking[item2] -= 0.1  # Image2 loses
        else:
            ranking[item2] += 0.1  # Image2 wins
            ranking[item1] -= 0.1  # Image1 loses

        rankings_history.append(ranking.copy())

    return rankings_history

# Step 4: Run Active Ranking Process
rankings_history = active_ranking(matches, initial_ranking, n_comparisons=100)

# Final Ranking - Ensure 'ranking' is a dictionary before sorting
ranking = {item: score for item, score in zip(items, ranking)}
final_ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

# Display the final ranking
print("Final Ranking of Images (from best to worst):")
for rank, (image, score) in enumerate(final_ranking, start=1):
    print(f"{rank}. {image} (Score: {score:.3f})")



"""### Bradley-Terry
https://github.com/lucasmaystre/choix/tree/master
"""

!pip install choix

import pandas as pd
import choix
import numpy as np

# Load the CSV file

# Prepare the data in a format suitable for the Bradley-Terry model
# We'll create a list of comparisons: (winner, loser)

# Step 1: Create a mapping from image labels to integer indices
unique_images = pd.concat([df['image1'], df['image2']]).unique()  # Get all unique image labels
image_to_idx = {image: idx for idx, image in enumerate(unique_images)}  # Map image labels to indices

# Step 2: Convert the image comparisons into integer indices
matches = []
for _, row in df.iterrows():
    image1 = row['image1']
    image2 = row['image2']
    selected = row['selected']

    idx1 = image_to_idx[image1]  # Convert image1 to its index
    idx2 = image_to_idx[image2]  # Convert image2 to its index

    if selected == image1:
        matches.append((idx1, idx2))  # image1 wins
    else:
        matches.append((idx2, idx1))  # image2 wins

# Now 'matches' contains a list of tuples like (winner, loser) with integer indices

# Step 3: Apply the Bradley-Terry model using ILSR with regularization
n_items = len(image_to_idx)  # Number of unique images (items)
print(f"Number of items (images): {n_items}")

params = choix.ilsr_pairwise(n_items, matches, alpha=0.01)

# Print the estimated parameters (strength/utility of each image)
print("Estimated strengths (abilities) of each image:")
print(params)

# Step 4: Ranking based on estimated strength (highest to lowest)
ranking = np.argsort(params)[::-1]  # Sort in descending order
print("Ranking of images (best to worst):")
for idx in ranking:
    print(f"{unique_images[idx]} (Strength: {params[idx]:.3f})")



"""### Kemeny's Method
Kemeny, J. G., & Snell, J. L. (1962). Mathematics of Social Choice. Duxbury Press.
"""

import pandas as pd
import itertools
import numpy as np
from collections import defaultdict

# Kemeny Ranking Method: Calculate the total number of disagreements for each possible ranking
def kemeny_ranking(df):
    # Get all unique designs (images)
    designs = set(df['image1']).union(set(df['image2']))

    # Create a dictionary to store the pairwise comparisons
    pairwise_comparisons = defaultdict(lambda: defaultdict(int))

    # Process each row in the CSV to populate pairwise comparisons
    for _, row in df.iterrows():
        image1 = row['image1']
        image2 = row['image2']
        selected = row['selected']

        if selected == image1:
            pairwise_comparisons[image1][image2] += 1
        else:
            pairwise_comparisons[image2][image1] += 1

    # Create all possible rankings (permutations) of the designs
    rankings = list(itertools.permutations(designs))

    # Calculate the total number of disagreements for each ranking
    def calculate_disagreements(ranking):
        disagreements = 0
        for i in range(len(ranking)):
            for j in range(i+1, len(ranking)):
                preferred = ranking[i]
                not_preferred = ranking[j]
                # Count the number of disagreements based on the pairwise comparisons
                disagreements += pairwise_comparisons[preferred].get(not_preferred, 0) + pairwise_comparisons[not_preferred].get(preferred, 0)
        return disagreements

    # Find the ranking with the minimum disagreements
    best_ranking = None
    min_disagreements = float('inf')
    for ranking in rankings:
        disagreements = calculate_disagreements(ranking)
        if disagreements < min_disagreements:
            min_disagreements = disagreements
            best_ranking = ranking

    # Return the best ranking
    return best_ranking

best_ranking = kemeny_ranking(df)
print("Best ranking based on Kemeny's method:")
print(best_ranking)

"""### Normalization"""

import pandas as pd
from collections import defaultdict

def rank_designs(df):

    # Dictionary to keep track of points and frequency of each image
    points = defaultdict(int)
    frequency = defaultdict(int)

    # Process each row in the CSV
    for index, row in df.iterrows():
        image1 = row['image1']
        image2 = row['image2']
        selected = row['selected']

        # Count frequency of each image
        frequency[image1] += 1
        frequency[image2] += 1

        # Assign points to the selected image
        if selected == image1:
            points[image1] += 1
        elif selected == image2:
            points[image2] += 1

    # Normalize points by frequency to reduce bias
    normalized_points = {}
    for image, score in points.items():
        normalized_points[image] = score / frequency[image]  # Normalize by frequency of appearance

    # Sort the designs based on normalized points in descending order
    ranked_designs = sorted(normalized_points.items(), key=lambda x: x[1], reverse=True)

    # Display the rankings
    print("Ranked Designs (from highest to lowest normalized points):")
    for rank, (design, score) in enumerate(ranked_designs, start=1):
        print(f"Rank {rank}: {design} with {score:.2f} normalized points")

    return ranked_designs

# Example usage:
rank_designs(df)

"""### Normalized Bradley-Terry"""

import pandas as pd
import numpy as np
import choix

# Load the CSV file

# Normalize the focus times for each image (min-max normalization)
# Step 1: Prepare the dataset to normalize focus times
focus_time_image1 = df['focus_time_image1']
focus_time_image2 = df['focus_time_image2']

# Combine focus times of image1 and image2 for min-max normalization
all_focus_times = np.concatenate([focus_time_image1, focus_time_image2])

# Min-max normalization function
def min_max_normalize(times):
    min_time = min(times)
    max_time = max(times)
    return [(time - min_time) / (max_time - min_time) if max_time > min_time else 0 for time in times]

# Normalize both focus times
df['normalized_focus_time_image1'] = min_max_normalize(focus_time_image1)
df['normalized_focus_time_image2'] = min_max_normalize(focus_time_image2)

# Step 2: Create the data for paired comparisons
# We will use the normalized focus times as a form of comparison weight
# Normalize the time (e.g., larger normalized value means the image was more focused on)

matches = []
for _, row in df.iterrows():
    image1 = row['image1']
    image2 = row['image2']
    selected = row['selected']

    normalized_focus_time1 = row['normalized_focus_time_image1']
    normalized_focus_time2 = row['normalized_focus_time_image2']

    if selected == image1:
        matches.append((image1, image2))  # image1 wins over image2
    else:
        matches.append((image2, image1))  # image2 wins over image1

# Step 3: Convert data into a format suitable for Bradley-Terry model
# Here, we are passing (winner, loser) where winner is the first item and loser is the second

n_items = len(df['image1'].unique())
print(f"Number of items (images): {n_items}")

# Mapping image labels to indices
unique_images = df['image1'].unique()
image_to_idx = {image: idx for idx, image in enumerate(unique_images)}

# Convert matches to indices
matches_indexed = [(image_to_idx[match[0]], image_to_idx[match[1]]) for match in matches]

# Step 4: Apply Bradley-Terry model using the ILSR algorithm with regularization
params = choix.ilsr_pairwise(n_items, matches_indexed, alpha=0.01)

# Print the estimated parameters (strength/utility of each image)
print("Estimated strengths (abilities) of each image:")
for i, param in enumerate(params):
    #print(f"Image {unique_images[i]} (Strength: {param:.3f})")
    pass

# Step 5: Ranking based on estimated strength (highest to lowest)
ranking = np.argsort(params)[::-1]  # Sort in descending order
print("Ranking of images (best to worst):")
for idx in ranking:
    print(f"Image {unique_images[idx]} (Strength: {params[idx]:.3f})")





