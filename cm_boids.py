import numpy as np
import random
from boids import Boid

class CollectiveMemoryBoid(Boid):
    def __init__(self, position, walls):
        super().__init__(position, walls)
        self.history = []
        self.history_length = 15
        self.individual_speed = random.uniform(0.8, 1.2)

    def flock(self, boids):
        base_behavior = super().flock(boids)
        memory_effect = np.zeros(2)
        if len(self.history) > 0:
            avg_historical_vector = np.mean(self.history, axis=0) - self.position
            memory_effect = avg_historical_vector * 0.05

        self.history.append(self.position.copy())
        if len(self.history) > self.history_length:
            self.history.pop(0)

        self.velocity *= self.individual_speed
        return base_behavior + memory_effect
