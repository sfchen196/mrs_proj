import pygame

# Screen dimensions
WIDTH, HEIGHT = 1080, 720

# Boid settings
NUM_BOIDS = 100
MAX_SPEED = 1
NEIGHBOR_RADIUS = 50
SEPARATION_RADIUS = 20

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Sliders for adjusting weights
ALIGNMENT_WEIGHT = 0.01
COHESION_WEIGHT = 0.001
SEPARATION_WEIGHT = 0.01

