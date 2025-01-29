import numpy as np
import random
from config import WIDTH, HEIGHT, MAX_SPEED, ALIGNMENT_WEIGHT, COHESION_WEIGHT, SEPARATION_WEIGHT, NEIGHBOR_RADIUS, SEPARATION_RADIUS
from walls import wall_positions, walls_visible

def limit_speed(velocity, max_speed):
    speed = np.linalg.norm(velocity)
    if speed > max_speed:
        return (velocity / speed) * max_speed
    return velocity

class Boid:
    def __init__(self, position):
        self.wall_positions = wall_positions
        self.position = np.array(position, dtype=float)  # Ensure position is float
        angle = random.uniform(0, 2 * np.pi)
        self.velocity = np.array([np.cos(angle), np.sin(angle)]) * MAX_SPEED

    def update(self, boids):
        acceleration = self.flock(boids)
        self.velocity += acceleration
        self.velocity = limit_speed(self.velocity, MAX_SPEED)
        self.position += self.velocity  # Update position
        self.bounce(boids)

    def bounce(self, boids):
        if self.is_touching_wall(self.wall_positions):
            if walls_visible:
                boids.remove(self)  # Remove the Boid from the list if it touches a wall
        else:
            if self.position[0] <= 0 or self.position[0] >= WIDTH:
                self.velocity[0] *= -1
            if self.position[1] <= 0 or self.position[1] >= HEIGHT:
                self.velocity[1] *= -1

    def is_touching_wall(self, wall_positions):
        for wall in wall_positions:
            if wall.collidepoint(self.position):
                return True
        return False

    def flock(self, boids):
        alignment = np.zeros(2)
        cohesion = np.zeros(2)
        separation = np.zeros(2)

        total = 0
        for other in boids:
            if other == self:  # Skip itself
                continue
            distance = np.linalg.norm(other.position - self.position)
            if distance < NEIGHBOR_RADIUS:
                alignment += other.velocity
                cohesion += other.position
                total += 1
                if distance < SEPARATION_RADIUS:
                    if distance > 0:  # Avoid division by zero
                        separation -= (other.position - self.position) / distance

        if total > 0:
            alignment /= total
            alignment = limit_speed(alignment, MAX_SPEED)
            cohesion = (cohesion / total - self.position) * COHESION_WEIGHT
            separation *= SEPARATION_WEIGHT
            alignment *= ALIGNMENT_WEIGHT

        return alignment + cohesion + separation
