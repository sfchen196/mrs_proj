import numpy as np
from boids import Boid, limit_speed
from config import MAX_SPEED

class DirectedBoid(Boid):
    def __init__(self, position, goal):
        super().__init__(position)
        self.goal = np.array(goal, dtype=float)

    def flock(self, boids):
        # 1. Get the base flocking behavior (includes wall avoidance, alignment, etc.)
        base_steering = super().flock(boids)

        # 2. Add steering towards the goal, with lower weight so wall avoidance still has effect
        goal_vector = self.goal - self.position
        goal_distance = np.linalg.norm(goal_vector)
        goal_steering = np.zeros(2)
        
        if goal_distance > 0:
            # Steering to turn toward the goal
            desired = limit_speed(goal_vector, MAX_SPEED)  # direction to goal
            goal_steering = desired - self.velocity
            goal_steering = limit_speed(goal_steering, MAX_SPEED)

        # 3. Blend the goal steering with the base steering
        # Here we give base_steering higher priority by weighting it more heavily.
        # You can tweak these ratios as needed.
        blend_ratio_base = 0.9
        blend_ratio_goal = 0.1
        
        behavior = blend_ratio_base * base_steering + blend_ratio_goal * goal_steering
        
        return behavior
