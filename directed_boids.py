import numpy as np
import config
from boids import Boid, limit_speed

class DirectedBoid(Boid):
    def __init__(self, position, goal):
        super().__init__(position)
        self.goal = np.array(goal, dtype=float)

    def flock(self, boids):
        base_force = super().flock(boids)
        goal_vector = self.goal - self.position
        goal_distance = np.linalg.norm(goal_vector)
        goal_force = np.zeros(2)
        if goal_distance > 0:
            desired = limit_speed(goal_vector, config.MAX_SPEED)
            goal_force = desired - self.velocity
            goal_force = limit_speed(goal_force, config.MAX_SPEED)
        return base_force + goal_force
