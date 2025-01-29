import pygame
from boids import Boid
from s_boids import DirectedBoid
from cm_boids import CollectiveMemoryBoid
from config import screen, clock, WIDTH, HEIGHT, NUM_BOIDS
from sliders import draw_sliders, handle_slider_events
from walls import walls_visible, wall_positions

def create_boids(use_directed=False, position=None, goal=None, use_collective_memory=False):
    if use_collective_memory:
        return [CollectiveMemoryBoid(position) for _ in range(NUM_BOIDS)]
    elif use_directed:
        return [DirectedBoid(position, goal) for _ in range(NUM_BOIDS)]
    else:
        return [Boid(position) for _ in range(NUM_BOIDS)]

def draw_walls(wall_positions):
    for wall in wall_positions:
        pygame.draw.rect(screen, (255, 255, 255), wall)

def draw_translucent_text(text, position, color, alpha):
    small_font = pygame.font.Font(None, 24)  # None uses the default font, size 24
    text_surface = small_font.render(text, True, color)
    text_surface.set_alpha(alpha)  # Set the translucency level
    screen.blit(text_surface, position)
