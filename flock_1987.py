import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

# Parameters
num_agents = 200
ks = 0.5  # Strength of spatial interaction
ka = 0.1  # Strength of velocity alignment
kf = 2.0  # Strength of the forcing function
dt = 0.1  # Time step
iterations = 1000

# Swarm initialization
positions = np.random.uniform(-10, 10, (num_agents, 2))  # Initial positions
velocities = np.random.uniform(-1, 1, (num_agents, 2))  # Initial velocities

# Gradient of the potential function to penalize closeness
def gradient_potential(distance_vec):
    distance = np.linalg.norm(distance_vec)
    if distance < 1.0:  # Too close
        return 2 * distance_vec / (distance + 1e-6)  # Repel
    elif distance < 5.0:  # Ideal distance
        return -distance_vec / (distance + 1e-6)  # Attract
    else:
        return np.zeros_like(distance_vec)  # No interaction

# Function to calculate forcing term to form a shape
# Here we use a predefined set of points forming "John Doe"
def forcing_function(positions, target_points):
    closest_targets = cdist(positions, target_points).argmin(axis=1)
    forces = target_points[closest_targets] - positions
    return kf * forces  # Amplify the forcing term

# Generate points for "John Doe" using text rendering
from PIL import Image, ImageDraw, ImageFont

def generate_text_points(text, font_size=200, scale=0.2):
    # Create an image and draw text
    font = ImageFont.load_default()
    image = Image.new('L', (1000, 400), color=0)
    draw = ImageDraw.Draw(image)
    draw.text((20, 100), text, fill=255, font=font)
    
    # Convert to points
    points = np.array(np.nonzero(np.array(image))).T
    points = points[:, [1, 0]]  # Flip x and y
    points = points - np.mean(points, axis=0)  # Center text
    points[:, 1] = -points[:, 1]  # Flip vertically to correct orientation
    points *= scale  # Scale to fit swarm size
    return points

text_points = generate_text_points("John Doe")

# Simulation loop
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(figsize=(8, 8))

for t in range(iterations):
    print(t)
    new_velocities = np.zeros_like(velocities)

    for i in range(num_agents):
        neighbors = np.linalg.norm(positions - positions[i], axis=1) < 5.0  # Neighborhood radius
        neighbors[i] = False  # Exclude self
        
        spatial_force = np.sum([
            ks * gradient_potential(positions[j] - positions[i]) for j in range(num_agents) if neighbors[j]
        ], axis=0)

        alignment_force = np.sum([
            ka * (velocities[j] - velocities[i]) for j in range(num_agents) if neighbors[j]
        ], axis=0)

        forcing_term = forcing_function(positions, text_points)

        # Update velocity
        new_velocities[i] = velocities[i] + dt * (spatial_force + alignment_force + forcing_term[i])

    velocities = new_velocities
    positions += velocities * dt

    # Plot swarm
    ax.clear()
    ax.scatter(positions[:, 0], positions[:, 1], s=10, color="blue")
    ax.scatter(text_points[:, 0], text_points[:, 1], s=1, color="red")
    ax.set_xlim(-5, 5)  # Fix x-axis limits
    ax.set_ylim(-5, 5)  # Fix y-axis limits
    ax.set_title(f"Swarm Simulation at Iteration {t}")
    plt.pause(0.01)

plt.ioff()
plt.show()