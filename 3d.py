import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from collections import deque

# Simulation parameters
NUM_BOIDS = 50
MAX_SPEED = 0.01
NEIGHBOR_RADIUS = 1.0
SEPARATION_RADIUS = 0.5
CUBE_SIZE = 8.0

# Boid weights
ALIGNMENT_WEIGHT = 0.05
COHESION_WEIGHT = 0.005
SEPARATION_WEIGHT = 0.05

class Boid:
    def __init__(self):
        self.position = np.random.uniform(-CUBE_SIZE/2, CUBE_SIZE/2, 3)
        direction = np.random.randn(3)
        self.velocity = direction / np.linalg.norm(direction) * MAX_SPEED

    def update(self, boids, Aro=5, Ara=10):
        r_r = 1
        r_o = r_r + Aro
        r_a = r_o + Ara
        
        repulsion = np.zeros(3)
        orientation = np.zeros(3)
        attraction = np.zeros(3)
        
        n_r = n_o = n_a = 0
        
        for other in boids:
            if other == self:
                continue
                
            distance = np.linalg.norm(other.position - self.position)
            
            if distance < r_r:
                repulsion -= (other.position - self.position) / (distance + 1e-8)
                n_r += 1
            elif distance < r_o:
                orientation += other.velocity
                n_o += 1
            elif distance < r_a:
                attraction += (other.position - self.position)
                n_a += 1
        
        acceleration = np.zeros(3)
        
        if n_r > 0:
            repulsion = repulsion / n_r
            acceleration = repulsion
        else:
            if n_o > 0:
                orientation = orientation / n_o
                acceleration += orientation * ALIGNMENT_WEIGHT
            
            if n_a > 0:
                attraction = attraction / n_a
                acceleration += attraction * COHESION_WEIGHT
        
        self.velocity += acceleration
        
        speed = np.linalg.norm(self.velocity)
        if speed > MAX_SPEED:
            self.velocity = (self.velocity / speed) * MAX_SPEED
            
        self.position += self.velocity
        
        for i in range(3):
            if self.position[i] > CUBE_SIZE/2:
                self.position[i] -= CUBE_SIZE
            elif self.position[i] < -CUBE_SIZE/2:
                self.position[i] += CUBE_SIZE

def draw_boid(boid):
    sphere = gluNewQuadric()
    glPushMatrix()
    glTranslatef(*boid.position)
    glColor3f(1, 1, 0)
    gluSphere(sphere, 0.1, 10, 10)
    glPopMatrix()

def draw_cube():
    glColor4f(1.0, 1.0, 1.0, 0.5)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vertices = [
        [-CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2],
        [ CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2],
        [ CUBE_SIZE/2,  CUBE_SIZE/2, -CUBE_SIZE/2],
        [-CUBE_SIZE/2,  CUBE_SIZE/2, -CUBE_SIZE/2],
        [-CUBE_SIZE/2, -CUBE_SIZE/2,  CUBE_SIZE/2],
        [ CUBE_SIZE/2, -CUBE_SIZE/2,  CUBE_SIZE/2],
        [ CUBE_SIZE/2,  CUBE_SIZE/2,  CUBE_SIZE/2],
        [-CUBE_SIZE/2,  CUBE_SIZE/2,  CUBE_SIZE/2]
    ]
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    glColor4f(0.8, 0.8, 0.8, 0.3)
    step = CUBE_SIZE / 10.0

    for i in range(-5, 6):
        pos = i * step
        
        glBegin(GL_LINES)
        glVertex3f(-CUBE_SIZE/2, -CUBE_SIZE/2, pos)
        glVertex3f(CUBE_SIZE/2, -CUBE_SIZE/2, pos)
        glVertex3f(pos, -CUBE_SIZE/2, -CUBE_SIZE/2)
        glVertex3f(pos, -CUBE_SIZE/2, CUBE_SIZE/2)
        
        glVertex3f(-CUBE_SIZE/2, CUBE_SIZE/2, pos)
        glVertex3f(CUBE_SIZE/2, CUBE_SIZE/2, pos)
        glVertex3f(pos, CUBE_SIZE/2, -CUBE_SIZE/2)
        glVertex3f(pos, CUBE_SIZE/2, CUBE_SIZE/2)
        
        glVertex3f(-CUBE_SIZE/2, pos, -CUBE_SIZE/2)
        glVertex3f(CUBE_SIZE/2, pos, -CUBE_SIZE/2)
        glVertex3f(pos, -CUBE_SIZE/2, -CUBE_SIZE/2)
        glVertex3f(pos, CUBE_SIZE/2, -CUBE_SIZE/2)
        
        glVertex3f(-CUBE_SIZE/2, pos, CUBE_SIZE/2)
        glVertex3f(CUBE_SIZE/2, pos, CUBE_SIZE/2)
        glVertex3f(pos, -CUBE_SIZE/2, CUBE_SIZE/2)
        glVertex3f(pos, CUBE_SIZE/2, CUBE_SIZE/2)
        
        glVertex3f(-CUBE_SIZE/2, -CUBE_SIZE/2, pos)
        glVertex3f(-CUBE_SIZE/2, CUBE_SIZE/2, pos)
        glVertex3f(-CUBE_SIZE/2, pos, -CUBE_SIZE/2)
        glVertex3f(-CUBE_SIZE/2, pos, CUBE_SIZE/2)
        
        glVertex3f(CUBE_SIZE/2, -CUBE_SIZE/2, pos)
        glVertex3f(CUBE_SIZE/2, CUBE_SIZE/2, pos)
        glVertex3f(CUBE_SIZE/2, pos, -CUBE_SIZE/2)
        glVertex3f(CUBE_SIZE/2, pos, CUBE_SIZE/2)
        glEnd()

class BoidsParameterAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        
    def _build_model(self):
        model = Sequential()
        model.add(Input(shape=(self.state_size,)))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return np.array([
                random.uniform(0, 15),
                random.uniform(0, 15)
            ])
        
        act_values = self.model.predict(state, verbose=0)
        return act_values[0]
    
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma * 
                          np.amax(self.model.predict(next_state, verbose=0)[0]))
            target_f = self.model.predict(state, verbose=0)
            target_f[0] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

def get_state(boids):
    positions = np.array([boid.position for boid in boids])
    velocities = np.array([boid.velocity for boid in boids])
    
    avg_direction = np.mean(velocities, axis=0)
    polarization = np.linalg.norm(avg_direction) / (np.mean(np.linalg.norm(velocities, axis=1)) + 1e-8)
    
    center = np.mean(positions, axis=0)
    rel_positions = positions - center
    cross_products = np.cross(rel_positions, velocities)
    angular_momentum = np.linalg.norm(np.mean(cross_products, axis=0))
    
    distances = []
    for i in range(len(boids)):
        for j in range(i+1, len(boids)):
            distances.append(np.linalg.norm(positions[i] - positions[j]))
    avg_distance = np.mean(distances) if distances else 0
    
    position_variance = np.mean(np.var(positions, axis=0))
    
    return np.array([[polarization, angular_momentum, avg_distance, position_variance]])

def calculate_reward(state, target_behavior):
    polarization = state[0][0]
    angular_momentum = state[0][1]
    avg_distance = state[0][2]
    position_variance = state[0][3]
    
    if target_behavior == "swarm":
        reward = (1 - polarization) * 0.5 + (1 - angular_momentum) * 0.5
    elif target_behavior == "torus":
        reward = (1 - polarization) * 0.5 + angular_momentum * 0.5
    elif target_behavior == "dynamic_parallel":
        reward = polarization * 0.6 + (1 - angular_momentum) * 0.3 + (position_variance / 10) * 0.1
    elif target_behavior == "highly_parallel":
        reward = polarization * 0.7 + (1 - angular_momentum) * 0.2 + (1 - position_variance / 5) * 0.1
    
    return reward

def train_boids_parameters(target_behavior, episodes=1000):
    state_size = 4
    action_size = 2
    agent = BoidsParameterAgent(state_size, action_size)
    
    batch_size = 32
    best_reward = -float('inf')
    best_params = None
    
    for e in range(episodes):
        initial_params = agent.act(np.zeros((1, state_size)))
        Aro, Ara = initial_params
        
        boids = [Boid() for _ in range(NUM_BOIDS)]
        
        for _ in range(500):
            for boid in boids:
                boid.update(boids, Aro=Aro, Ara=Ara)
        
        state = get_state(boids)
        
        total_reward = 0
        for _ in range(100):
            for boid in boids:
                boid.update(boids, Aro=Aro, Ara=Ara)
            
            next_state = get_state(boids)
            reward = calculate_reward(next_state, target_behavior)
            total_reward += reward
            
            agent.remember(state, initial_params, reward, next_state, False)
            state = next_state
        
        agent.remember(state, initial_params, total_reward, state, True)
        
        if len(agent.memory) > batch_size:
            agent.replay(batch_size)
        
        if total_reward > best_reward:
            best_reward = total_reward
            best_params = (Aro, Ara)
        
        print(f"Episode: {e+1}/{episodes}, Reward: {total_reward}, Best Params: {best_params}")
    
    return best_params

def visualize_learned_behavior(params, behavior_name):
    Aro, Ara = params
    
    boids = [Boid() for _ in range(NUM_BOIDS)]
    
    for _ in range(500):
        for boid in boids:
            boid.update(boids, Aro=Aro, Ara=Ara)
    
    pygame.init()
    display = (1080, 720)
    pygame.display.set_mode(display, pygame.DOUBLEBUF|pygame.OPENGL)
    pygame.display.set_caption(f"Learned {behavior_name} Behavior")
    
    gluPerspective(45, display[0]/display[1], 0.1, 50.0)
    glTranslatef(0.0, 0.0, -15)
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        for boid in boids:
            boid.update(boids, Aro=Aro, Ara=Ara)
            draw_boid(boid)
        
        draw_cube()
        pygame.display.flip()
        clock.tick(60)

def main():
    behaviors = ["swarm", "torus", "dynamic_parallel", "highly_parallel"]
    learned_params = {}
    
    for behavior in behaviors:
        print(f"\nTraining parameters for {behavior} behavior...")
        params = train_boids_parameters(behavior, episodes=200)
        learned_params[behavior] = params
        print(f"Best parameters for {behavior}: {params}")
    
    import json
    with open("learned_boid_parameters.json", "w") as f:
        json.dump(learned_params, f)
    
    for behavior in behaviors:
        visualize_learned_behavior(learned_params[behavior], behavior)

if __name__ == "__main__":
    main()
