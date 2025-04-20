import numpy as np
import random
import config
import walls
from directed_boids import DirectedBoid
from boids import limit_speed
from number_inputs import selected_params, nonselected_params

class HeteroDirectedBoid(DirectedBoid):
    """
    A heterogeneous directed boid that inherits goal-seeking behavior from DirectedBoid
    and wall avoidance from Boid. Depending on the 'selected' flag, it uses parameters
    from either selected_params or nonselected_params.
    """
    def __init__(self, position, goal, selected=False):
        super().__init__(position, goal)
        self.selected = selected
        if not self.selected:
            # Randomly vary individual parameters.
            self.max_speed = config.MAX_SPEED * random.uniform(0.8, 1.2)
            self.neighbor_radius = config.NEIGHBOR_RADIUS * random.uniform(0.8, 1.2)
            self.separation_radius = config.SEPARATION_RADIUS * random.uniform(0.8, 1.2)
            self.ALIGNMENT_WEIGHT = config.ALIGNMENT_WEIGHT * random.uniform(0.8, 1.2)
            self.COHESION_WEIGHT = config.COHESION_WEIGHT * random.uniform(0.8, 1.2)
            self.SEPARATION_WEIGHT = config.SEPARATION_WEIGHT * random.uniform(0.8, 1.2)
            self.turning_rate = random.uniform(np.radians(10), np.radians(30))
        else:
            # Selected boids use global parameters.
            self.max_speed = config.MAX_SPEED
            self.neighbor_radius = config.NEIGHBOR_RADIUS
            self.separation_radius = config.SEPARATION_RADIUS
            self.ALIGNMENT_WEIGHT = config.ALIGNMENT_WEIGHT
            self.COHESION_WEIGHT = config.COHESION_WEIGHT
            self.SEPARATION_WEIGHT = config.SEPARATION_WEIGHT
            self.turning_rate = np.radians(15)

    def flock(self, boids):
        wall_avoidance = self.avoid_walls()
        alignment = np.zeros(2)
        cohesion = np.zeros(2)
        separation = np.zeros(2)
        total = 0

        # Choose parameter set based on whether this boid is selected.
        if self.selected:
            neighbor_rad = selected_params["NEIGHBOR_RADIUS"]
            separation_rad = selected_params["SEPARATION_RADIUS"]
            align_weight = selected_params["ALIGNMENT_WEIGHT"]
            cohesion_weight = selected_params["COHESION_WEIGHT"]
            separation_weight = selected_params["SEPARATION_WEIGHT"]
            current_max_speed = selected_params["MAX_SPEED"]
        else:
            neighbor_rad = nonselected_params["NEIGHBOR_RADIUS"]
            separation_rad = nonselected_params["SEPARATION_RADIUS"]
            align_weight = nonselected_params["ALIGNMENT_WEIGHT"]
            cohesion_weight = nonselected_params["COHESION_WEIGHT"]
            separation_weight = nonselected_params["SEPARATION_WEIGHT"]
            current_max_speed = nonselected_params["MAX_SPEED"]

        for other in boids:
            if other == self:
                continue
            distance = np.linalg.norm(other.position - self.position)
            if distance < neighbor_rad:
                alignment += other.velocity
                cohesion += other.position
                total += 1
            if distance < separation_rad:
                if distance > 0:
                    separation -= (other.position - self.position) / distance

        if total > 0:
            alignment /= total
            alignment = limit_speed(alignment, current_max_speed)
            cohesion = (cohesion / total - self.position) * cohesion_weight

        separation *= separation_weight
        alignment *= align_weight
        base_flock = wall_avoidance + alignment + cohesion + separation

        # Add goal-steering force from DirectedBoid.
        goal_vector = self.goal - self.position
        goal_distance = np.linalg.norm(goal_vector)
        goal_force = np.zeros(2)
        if goal_distance > 0:
            desired = limit_speed(goal_vector, current_max_speed)
            goal_force = desired - self.velocity
            goal_force = limit_speed(goal_force, current_max_speed)
        return base_flock + goal_force

    def update(self, boids):
        acceleration = self.flock(boids)
        desired_velocity = self.velocity + acceleration

        current_angle = np.arctan2(self.velocity[1], self.velocity[0])
        desired_angle = np.arctan2(desired_velocity[1], desired_velocity[0])
        angle_diff = (desired_angle - current_angle + np.pi) % (2 * np.pi) - np.pi
        if abs(angle_diff) > self.turning_rate:
            angle_diff = np.sign(angle_diff) * self.turning_rate
        new_angle = current_angle + angle_diff

        if self.selected:
            current_max_speed = selected_params["MAX_SPEED"]
        else:
            current_max_speed = nonselected_params["MAX_SPEED"]

        new_speed = np.linalg.norm(desired_velocity)
        self.velocity = np.array([np.cos(new_angle), np.sin(new_angle)]) * min(new_speed, current_max_speed)
        self.position += self.velocity

        if walls.walls_visible:
            if self.is_touching_wall(self.wall_positions):
                boids.remove(self)

        if self.position[0] < 0:
            self.position[0] = config.WIDTH
        elif self.position[0] > config.WIDTH:
            self.position[0] = 0
        if self.position[1] < 0:
            self.position[1] = config.HEIGHT
        elif self.position[1] > config.HEIGHT:
            self.position[1] = 0
