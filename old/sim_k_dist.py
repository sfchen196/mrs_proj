import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.stats import spearmanr

# --- Initialization functions ---

def initialize_positions(N=30, radius=1.0):
    """
    Place N agents uniformly at random in a circle of a given radius.
    Returns a NumPy array of shape (N, 2).
    """
    angles = 2 * np.pi * np.random.rand(N)
    radii = radius * np.sqrt(np.random.rand(N))
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return np.column_stack((x, y))

def initialize_k_values(N=30, k_min=1, k_max=10, mean=5.5, std=2.0):
    """
    Assign each boid an individual neighborhood size (k) sampled from a normal distribution.
    The resulting values are rounded and clipped between k_min and k_max.
    """
    k_values = np.random.normal(loc=mean, scale=std, size=N)
    k_values = np.rint(k_values).astype(int)
    return np.clip(k_values, k_min, k_max)

def k_nearest_neighbors(positions, focal_idx, k):
    """
    Return the indices of the k nearest neighbors of the focal individual.
    """
    focal_pos = positions[focal_idx]
    dists = np.linalg.norm(positions - focal_pos, axis=1)
    dists[focal_idx] = np.inf  # ignore self
    return np.argsort(dists)[:min(k, len(positions)-1)]

# --- Modified step function with repulsion ---
def step(positions, k_values, p=0.1, step_size=0.01, noise_scale=0.02,
         repulsion_radius=0.1, repulsion_strength=0.05):
    """
    One simulation timestep with two forces:
      - With probability p, the boid takes a random step.
      - Otherwise, it moves toward the centroid of its personal k nearest neighbors.
      - Additionally, any boid found within 'repulsion_radius' yields a repulsive force,
        preventing the boids from collapsing to a single point.
    """
    N = len(positions)
    new_positions = positions.copy()
    
    for i in range(N):
        if np.random.rand() < p:
            new_positions[i] += noise_scale * np.random.randn(2)
        else:
            personal_k = k_values[i]
            neighbors = k_nearest_neighbors(positions, i, personal_k)
            nbr_centroid = np.mean(positions[neighbors], axis=0)
            attract_direction = nbr_centroid - positions[i]
            norm_attr = np.linalg.norm(attract_direction)
            if norm_attr > 1e-9:
                attract_force = (step_size * attract_direction) / norm_attr
            else:
                attract_force = 0

            # Compute repulsive force from all boids that are too close.
            repulsive_force = np.zeros(2)
            for j in range(N):
                if j == i:
                    continue
                d = np.linalg.norm(positions[j] - positions[i])
                if d < repulsion_radius and d > 1e-9:
                    # The closer the boid, the stronger the repulsion.
                    repulsive_force += (positions[i] - positions[j]) / d * (repulsion_radius - d)
            # Weight the repulsion term.
            repulsive_force *= repulsion_strength

            # Combine attraction and repulsion.
            total_force = attract_force + repulsive_force
            new_positions[i] += total_force
    return new_positions

def average_distances(positions):
    """
    Compute the distance of each boid from the group centroid.
    Returns distances and the centroid.
    """
    centroid = np.mean(positions, axis=0)
    distances = np.linalg.norm(positions - centroid, axis=1)
    return distances, centroid

# --- Simulation parameters ---
N = 30              # Number of boids
p = 0.1             # Probability of random step
step_size = 0.01    # Attractive step size toward neighbor centroid
noise_scale = 0.02  # Random step noise scale
radius = 1.0        # Initial distribution radius
steps = 2000        # Total animation frames

repulsion_radius = 0.1  # Distance under which boids repel each other
repulsion_strength = 0.05  # Strength scaling for repulsion force

# Initialize positions and individual k values from a normal distribution.
positions = initialize_positions(N, radius)
k_values = initialize_k_values(N, k_min=1, k_max=10, mean=5.5, std=2.0)

# For visualization: map each boid's k value to color.
k_min_val, k_max_val = 1, 10
norm_k = (k_values - k_min_val) / (k_max_val - k_min_val)
cmap = plt.get_cmap("viridis")
colors = cmap(norm_k)

# --- Set up the matplotlib figure ---
fig, ax = plt.subplots(figsize=(7, 7))
scat = ax.scatter(positions[:, 0], positions[:, 1], c=colors, s=50,
                  edgecolors='k', label='Boids')
centroid_point, = ax.plot([], [], 'ro', markersize=8, label='Centroid')
ax.set_xlim(-1.5*radius, 1.5*radius)
ax.set_ylim(-1.5*radius, 1.5*radius)
ax.set_aspect('equal')
title_text = ax.text(0.02, 0.95, '', transform=ax.transAxes,
                     fontsize=12, verticalalignment='top')
ax.legend(loc='upper right')

# --- Data for aggregate plots ---
aggregate_frames = []
aggregate_mean_dists = []
aggregate_spearman = []

# --- Animation update function ---
def update(frame):
    global positions
    positions = step(positions, k_values, p=p, step_size=step_size,
                     noise_scale=noise_scale, repulsion_radius=repulsion_radius,
                     repulsion_strength=repulsion_strength)
    scat.set_offsets(positions)
    
    # Calculate group centroid and distances.
    distances, centroid = average_distances(positions)
    centroid_point.set_data([centroid[0]], [centroid[1]])
    
    # Compute Spearman correlation between individual k and distance.
    corr, _ = spearmanr(k_values, distances)
    mean_dist = np.mean(distances)
    
    title_text.set_text(f"Frame: {frame} | Spearman r = {corr:.3f} | Mean Dist = {mean_dist:.3f}")
    
    aggregate_frames.append(frame)
    aggregate_mean_dists.append(mean_dist)
    aggregate_spearman.append(corr)
    
    return scat, centroid_point, title_text

# --- Event handler to stop animation ---
def on_key_press(event):
    if event.key == 'escape':
        anim.event_source.stop()
        plt.close(fig)
        plot_aggregate()

def plot_aggregate():
    """
    Plot the aggregate results after simulation stops:
      - Scatter plot: each boid's k vs. its final distance from the centroid.
      - Time evolution plots for mean distance and Spearman correlation.
    """
    final_distances, _ = average_distances(positions)
    sp_corr, _ = spearmanr(k_values, final_distances)
    
    # Scatter plot of k vs. final distance.
    plt.figure(figsize=(7,5))
    plt.scatter(k_values, final_distances, c=k_values, cmap='viridis', edgecolor='k')
    plt.xlabel("Neighborhood Size (k)")
    plt.ylabel("Distance from Group Centroid")
    plt.title(f"Aggregate Graph: Spearman r = {sp_corr:.3f}")
    plt.colorbar(label="k value")
    plt.show()
    
    # Mean distance evolution.
    plt.figure(figsize=(7,5))
    plt.plot(aggregate_frames, aggregate_mean_dists, linestyle='--', color='blue')
    plt.xlabel("Frame")
    plt.ylabel("Mean Distance from Centroid")
    plt.title("Mean Distance Evolution Over Time")
    plt.show()
    
    # Spearman correlation evolution.
    plt.figure(figsize=(7,5))
    plt.plot(aggregate_frames, aggregate_spearman, linestyle='-', color='green')
    plt.xlabel("Frame")
    plt.ylabel("Spearman Correlation")
    plt.title("Spearman Correlation Evolution Over Time")
    plt.show()

# --- Connect key press event ---
fig.canvas.mpl_connect('key_press_event', on_key_press)

# --- Create and run the animation ---
anim = FuncAnimation(fig, update, frames=steps, interval=30, blit=True)
plt.title("Real-Time Boid Movement with Individual k Values and Repulsion\n(Press 'Escape' to exit and view aggregate graphs)")
plt.show()
