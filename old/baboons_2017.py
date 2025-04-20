import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
NUM_BOTS = 30  # Number of bots
SPACE_SIZE = 10  # Size of the space (10x10)
TIME_STEPS = 200  # Number of time steps
STEP_SIZE = 0.05  # Maximum step size
# PROB_RANDOM_MOVE = 0.2  # Probability of random movement
PROB_RANDOM_MOVE = 0.5  # Probability of random movement

# Initialize positions and neighborhood sizes
positions = np.random.rand(NUM_BOTS, 2) * SPACE_SIZE
# neighborhood_sizes = np.random.randint(1, 5, size=NUM_BOTS)
neighborhood_sizes = np.random.randint(1, 5, size=NUM_BOTS)

# Function to compute the centroid of the k nearest neighbors
def compute_centroid(bot_index, positions, k):
    distances = np.linalg.norm(positions - positions[bot_index], axis=1)
    nearest_neighbors = np.argsort(distances)[1:k + 1]  # Exclude itself
    centroid = positions[nearest_neighbors].mean(axis=0)
    return centroid

# Update function for movement
def update_positions(positions, neighborhood_sizes):
    new_positions = positions.copy()
    for i in range(len(positions)):
        if np.random.rand() < PROB_RANDOM_MOVE:
            # Random movement
            new_positions[i] += (np.random.rand(2) - 0.5) * STEP_SIZE
        else:
            # Move towards the centroid of k nearest neighbors
            k = neighborhood_sizes[i]
            centroid = compute_centroid(i, positions, k)
            direction = centroid - positions[i]
            if np.linalg.norm(direction) > 0:  # Avoid division by zero
                step = direction / np.linalg.norm(direction) * STEP_SIZE
                new_positions[i] += step

        # Ensure positions stay within bounds
        new_positions[i] = np.clip(new_positions[i], 0, SPACE_SIZE)
    return new_positions

# Visualization setup
fig, ax = plt.subplots()
ax.set_xlim(0, SPACE_SIZE)
ax.set_ylim(0, SPACE_SIZE)
circles = [plt.Circle((0, 0), 0.2, color='blue', alpha=0.6) for _ in range(NUM_BOTS)]
labels = [ax.text(0, 0, str(neighborhood_sizes[i]), color='black', fontsize=8, ha='center', va='center') for i in range(NUM_BOTS)]
for circle in circles:
    ax.add_patch(circle)

# Update function for animation
def animate(frame):
    global positions
    positions = update_positions(positions, neighborhood_sizes)  # Corrected reassignment
    for i, circle in enumerate(circles):
        circle.center = positions[i]
    for i, label in enumerate(labels):
        label.set_position(positions[i])
    return circles + labels

# Run animation as a live video
ani = FuncAnimation(fig, animate, frames=TIME_STEPS, interval=50, blit=True)
plt.show()

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation

# # Parameters
# NUM_BOTS = 20  # Number of bots
# SPACE_SIZE = 10  # Size of the space (10x10)
# TIME_STEPS = 200  # Number of time steps
# STEP_SIZE = 0.1  # Maximum step size
# PROB_RANDOM_MOVE = 0.6  # Probability of random movement

# # New parameters for distance-based behavior
# REPULSION_DISTANCE = 0.5
# ATTRACTION_DISTANCE = 3.0

# # Initialize positions and neighborhood sizes
# positions = np.random.rand(NUM_BOTS, 2) * SPACE_SIZE
# neighborhood_sizes = np.random.randint(1, 8, size=NUM_BOTS)

# def compute_centroid(bot_index, positions, k):
#     """Return the centroid (average position) of the k nearest neighbors of bot_index."""
#     distances = np.linalg.norm(positions - positions[bot_index], axis=1)
#     nearest_neighbors = np.argsort(distances)[1:k+1]  # Exclude the bot itself
#     centroid = positions[nearest_neighbors].mean(axis=0)
#     return centroid

# def update_positions(positions, neighborhood_sizes):
#     new_positions = positions.copy()
#     for i in range(len(positions)):
#         # Random movement with probability PROB_RANDOM_MOVE
#         if np.random.rand() < PROB_RANDOM_MOVE:
#             new_positions[i] += (np.random.rand(2) - 0.5) * STEP_SIZE
#         else:
#             # Otherwise, move based on distance to the centroid
#             k = neighborhood_sizes[i]
#             centroid = compute_centroid(i, positions, k)
#             direction = centroid - positions[i]
#             distance = np.linalg.norm(direction)

#             if distance > 0:
#                 # Repulsion if too close
#                 if distance < REPULSION_DISTANCE:
#                     step = -(direction / distance) * STEP_SIZE
#                 # Attraction if too far
#                 elif distance > ATTRACTION_DISTANCE:
#                     step = (direction / distance) * STEP_SIZE
#                 else:
#                     # If within comfortable range, do nothing (or implement alignment, etc.)
#                     step = np.zeros(2)
#                 new_positions[i] += step

#         # Keep positions within bounds
#         new_positions[i] = np.clip(new_positions[i], 0, SPACE_SIZE)
#     return new_positions

# # Visualization setup
# fig, ax = plt.subplots()
# ax.set_xlim(0, SPACE_SIZE)
# ax.set_ylim(0, SPACE_SIZE)

# # Use circles to represent the bots
# circles = [plt.Circle((0, 0), 0.2, color='blue', alpha=0.6) for _ in range(NUM_BOTS)]
# for circle in circles:
#     ax.add_patch(circle)

# # Text label to show each bot’s neighborhood size (just for clarity)
# labels = [
#     ax.text(0, 0, str(neighborhood_sizes[i]), color='black', fontsize=8, 
#             ha='center', va='center') 
#     for i in range(NUM_BOTS)
# ]

# def animate(frame):
#     global positions
#     positions = update_positions(positions, neighborhood_sizes)
#     for i, circle in enumerate(circles):
#         circle.center = positions[i]
#     for i, label in enumerate(labels):
#         label.set_position(positions[i])
#     return circles + labels

# ani = FuncAnimation(fig, animate, frames=TIME_STEPS, interval=50, blit=True)
# plt.show()
