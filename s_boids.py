import numpy as np
from boids import Boid, limit_speed
from config import MAX_SPEED

class DirectedBoid(Boid):
    def __init__(self, position, goal):
        super().__init__(position)
        self.goal = np.array(goal, dtype=float)  # Ensure goal is float

    def flock(self, boids):
        # Get the base flocking behavior
        behavior = super().flock(boids)

        # Add steering towards the goal
        goal_vector = self.goal - self.position
        goal_distance = np.linalg.norm(goal_vector)
        if goal_distance > 0:
            goal_vector = limit_speed(goal_vector, MAX_SPEED)
            steering = goal_vector - self.velocity
            steering = limit_speed(steering, MAX_SPEED)
            behavior += steering  # Add steering towards the goal

        return behavior
