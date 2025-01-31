## Overview
This repository demonstrates a basic *Boids* flocking simulation, showing how individual agents (boids) exhibit collective behavior based on local interaction rules. The simulation allows you to toggle between different modes: standard boids, directed boids, and collective memory boids. It also supports toggling walls on/off and includes a simple slider-based interface to adjust parameters like speed, alignment, cohesion, separation, neighbor radius, and separation radius.

## Core Concepts
Flocking behavior is typically broken down into three basic steering rules, often referred to collectively as "separation, alignment, and cohesion"[1][2]:

1. **Separation:** Steer to avoid crowding neighbors.

The separation vector is calculated as a sum of normalized vectors pointing away from each neighbor, weighted inversely by distance. This creates a stronger repulsion from closer neighbors and weaker from distant ones. The negative sign ensures the force pushes away from neighbors rather than toward them.

2. **Alignment:** Steer towards the average heading of neighbors.

The alignment vector represents velocity matching, computed as the mean velocity of all neighbors. This average naturally dampens erratic movements since extreme velocities get averaged out with more moderate ones. The resulting vector provides a target velocity that the boid should gradually steer toward.

3. **Cohesion:** Steer to move toward the average position of neighbors.

The cohesion vector is calculated by first finding the center of mass (average position) of all neighbors, then creating a vector from the current boid's position to this center. This difference vector naturally points toward the group's center with a magnitude proportional to how far the boid is from the group.

Mathematically, let each boid have position $\mathbf{x}_i$ and velocity $\mathbf{v}_i$. If $\mathcal{N}(i)$ is the set of neighbors of boid $i$, then we often define:

$$
\mathbf{v}_\text{align}(i) = \frac{1}{|\mathcal{N}(i)|} \sum_{j \in \mathcal{N}(i)} \mathbf{v}_j
$$


$$
\mathbf{v}_\text{cohesion}(i) = \left(\frac{1}{|\mathcal{N}(i)|} \sum_{j \in \mathcal{N}(i)} \mathbf{x}_j\right) - \mathbf{x}_i
$$


$$
\mathbf{v}_\text{separation}(i) = -\sum_{j \in \mathcal{N}(i)} \frac{\mathbf{x}_j - \mathbf{x}_i}{\|\mathbf{x}_j - \mathbf{x}_i\|}
$$


In practice, these vectors are scaled by configurable weights and combined to update the boid’s velocity.


The alignment vector $\mathbf{v}\text{align}(i)$ represents the average velocity of neighboring boids, effectively matching speed and direction with the group. The cohesion vector $\mathbf{v}\text{cohesion}(i)$ points from the current boid's position to the center of mass of its neighbors, creating a tendency to stay with the group. The separation vector $\mathbf{v}_\text{separation}(i)$ creates a repulsive force that grows stronger as boids get closer, with the inverse distance relationship ensuring nearby neighbors have a stronger influence than distant ones.

## Code Structure

**boids.py**  
This file defines the main Boid class and its associated functions:
- `Boid.__init__`: Initializes a boid with a random velocity and a specified start position.  
- `update`: Performs one simulation step for the boid, combining behavior forces (alignment, cohesion, and separation) with wall avoidance before updating its position.  
- `flock`: Calculates and sums the steering vectors for alignment, cohesion, and separation, also incorporating wall avoidance.  
- `limit_speed`: Ensures the velocity does not exceed a specified maximum.  
- `bounce`: Handles collision with screen edges or removal if walls are active and the boid touches a wall.

**s_boids.py**  
Defines a `DirectedBoid` class, which inherits from `Boid`. This variant includes a specific target goal. The flocking behavior is extended to steer slightly toward the goal while still respecting alignment, cohesion, and separation. To blend the goal-directed velocity and standard flocking velocity, we use a factor $\alpha$ such that:

$$
\mathbf{v}_\text{directed}(i) = \alpha \,\mathbf{v}_\text{goal}(i) + (1 - \alpha)\,\mathbf{v}_\text{flock}(i)
$$


where $\mathbf{v}_\text{goal}(i)$ is the velocity component steering toward the selected goal, and $\mathbf{v}_\text{flock}(i)$ is the combined alignment, cohesion, and separation velocity term.

**main.py**  
- Implements the main application loop using pygame.  
- Provides a menu and the ability to choose between standard boids, directed boids, or a collective memory variant.  
- Lets you toggle walls, set new goals by clicking with the mouse, and returns to the menu by pressing Esc.  
- Draws boids on screen, updates them each frame, and allows adjusting simulation parameters using sliders.

**viz.py**  
- Contains visualization helpers to create boids, render text to the screen, and draw wall rectangles when enabled.  
- The `create_boids` function centralizes boid creation for the different modes, returning either normal boids, directed boids, or collective memory boids depending on chosen simulation type.

## Configuration Files

**config.py**
This file contains key simulation parameters that can be modified:

- Screen dimensions (WIDTH, HEIGHT): Adjust for different window sizes
- NUM_BOIDS: Change the total number of simulated boids
- MAX_SPEED: Set the maximum velocity limit
- NEIGHBOR_RADIUS: Define the perception range for flocking
- SEPARATION_RADIUS: Set the minimum distance between boids
- Weight parameters: Fine-tune ALIGNMENT_WEIGHT, COHESION_WEIGHT, and SEPARATION_WEIGHT

**walls.py**
Defines obstacle configurations using pygame.Rect objects. The file includes:

- Border walls around the screen edges
- Various shapes (plus sign, inverted T, I shape, L shape, H shape)
- A walls_visible flag to toggle obstacle visibility

Customization options:
- Add new wall shapes using pygame.Rect(x, y, width, height)
- Modify existing wall positions by adjusting coordinates
- Change wall dimensions by altering the rectangle sizes
- Create dynamic patterns by modifying the wall_positions list

**sliders.py**
Implements an interactive GUI for real-time parameter adjustment:

- Slider controls for speed, alignment, cohesion, separation
- Additional sliders for neighbor and separation radius
- Visual feedback with different colors for each parameter
- Labels and value display

## Adjusting Parameters
- **Speed**: Controls the maximum velocity limit of each boid.  
- **Alignment Weight**: Scales how strongly a boid aligns its velocity to neighbors.  
- **Cohesion Weight**: Adjusts the tendency of a boid to move toward the group’s centroid.  
- **Separation Weight**: Determines how strongly a boid avoids getting too close to neighbors.  
- **Neighbor Radius**: The perception range for detecting neighbor boids when calculating alignment or cohesion.  
- **Separation Radius**: The distance threshold under which boids will actively steer to separate from each other.  

These parameters can be tuned for different flocking patterns.

## Walls and Obstacle Avoidance
When walls are enabled, they are treated as obstacles that can reflect or remove boids upon collision. In the code, a wall-induced steering vector can be modeled by a simple repulsive force:

$$
\mathbf{v}_\text{wall}(i) = -k \sum_{w \in \mathcal{W}} \frac{\mathbf{x}_i - \mathbf{x}_w}{\|\mathbf{x}_i - \mathbf{x}_w\|}
$$


where $\mathcal{W}$ is the set of wall boundary points, $k$ is a constant scaling factor, and $\mathbf{x}_w$ is a point on a wall. This force is added to the boid’s velocity if it is within a certain threshold distance from the wall, pushing the boid away to avoid collision.

## How to Run
1. Ensure you have pygame and numpy installed.  
2. Run `main.py` to launch the flocking simulation.  
3. Press **1**, **2**, or **3** to select the flocking mode.  
4. Press **W** to toggle wall visibility.  
5. Click on the screen to set positions or goals (depending on the selected mode).  
6. Use the sliders to adjust flocking behaviors.

Enjoy exploring this simulation and experiment with the configurations to observe emergent flocking patterns!

## References:

[1] Reynolds, C.W., 1987, August. Flocks, herds and schools: A distributed behavioral model. In Proceedings of the 14th annual conference on Computer graphics and interactive techniques (pp. 25-34).

[2] Reynolds, C.W., 1999, March. Steering behaviors for autonomous characters. In Game developers conference (Vol. 1999, pp. 763-782).
