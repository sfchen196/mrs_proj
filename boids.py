import numpy as np
import random
import config
import walls

def limit_speed(velocity, max_speed=None):
    if max_speed is None:
        max_speed = config.MAX_SPEED
    speed = np.linalg.norm(velocity)
    if speed > max_speed:
        return (velocity / speed) * max_speed
    return velocity

class Boid:
    def __init__(self, position):
        self.wall_positions = walls.wall_positions
        self.position = np.array(position, dtype=float)
        angle = random.uniform(0, 2 * np.pi)
        self.velocity = np.array([np.cos(angle), np.sin(angle)]) * config.MAX_SPEED

    def update(self, boids):
        # Combine all steering behaviors (wall avoidance has highest priority)
        acceleration = self.flock(boids)
        self.velocity += acceleration
        self.velocity = limit_speed(self.velocity)
        self.position += self.velocity
        
        # Remove wall touching boids
        if walls.walls_visible:
            if self.is_touching_wall(self.wall_positions):
                boids.remove(self)

        # Toroidal wrap-around logic
        if self.position[0] < 0:
            self.position[0] = config.WIDTH
        elif self.position[0] > config.WIDTH:
            self.position[0] = 0
            
        if self.position[1] < 0:
            self.position[1] = config.HEIGHT
        elif self.position[1] > config.HEIGHT:
            self.position[1] = 0        

    def is_touching_wall(self, wall_positions):
        for wall in wall_positions:
            if wall.collidepoint(self.position):
                return True
        return False

    def flock(self, boids):
        # 1. Wall avoidance (highest priority)
        wall_avoidance = self.avoid_walls()

        # 2. Alignment, cohesion, and separation
        alignment = np.zeros(2)
        cohesion = np.zeros(2)
        separation = np.zeros(2)
        total = 0
        for other in boids:
            if other == self:
                continue
            distance = np.linalg.norm(other.position - self.position)

            if distance < config.NEIGHBOR_RADIUS:
                alignment += other.velocity
                cohesion += other.position
                total += 1

            if distance < config.SEPARATION_RADIUS:
                if distance > 0:
                    separation -= (other.position - self.position) / distance

        if total > 0:
            # Average alignment steering
            alignment /= total
            alignment = limit_speed(alignment)

            # Cohesion steering
            cohesion = (cohesion / total - self.position) * config.COHESION_WEIGHT

        # Scale separation and alignment
        separation *= config.SEPARATION_WEIGHT
        alignment *= config.ALIGNMENT_WEIGHT

        # Sum all forces
        return wall_avoidance + alignment + cohesion + separation

    def avoid_walls(self):
        # Returns a steering force that steers away from nearby walls (priority-based obstacle avoidance[1])
        if not walls.walls_visible:
            return np.zeros(2)

        print(walls.walls_visible)
        avoidance_force = np.zeros(2)
        avoid_distance = 50.0  # Distance threshold for wall avoidance
        for rect in self.wall_positions:
            # Find the closest point on the wall rectangle to the boid
            closest_x = max(rect.left, min(self.position[0], rect.right))
            closest_y = max(rect.top, min(self.position[1], rect.bottom))
            diff = self.position - np.array([closest_x, closest_y])
            dist = np.linalg.norm(diff)
            # If within avoidance distance, push away
            if dist < avoid_distance and dist > 0:
                # Increase force the closer we are to the wall
                push_strength = (avoid_distance - dist) / avoid_distance
                avoidance_force += (diff / dist) * push_strength

        # You can adjust this weight if needed
        avoidance_weight = 1.0
        avoidance_force *= avoidance_weight
        return avoidance_force
