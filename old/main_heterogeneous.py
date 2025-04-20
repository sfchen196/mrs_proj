import pygame
import config
from hetero_boids import HeteroBoid
import walls
from viz import screen, clock, draw_translucent_text, draw_walls
from sliders import (speed_slider, alignment_slider, cohesion_slider,
                     separation_slider, neighbor_radius_slider, separation_radius_slider,
                     draw_sliders, handle_slider_events)
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# Number of boids that are selected (highlighted) using slider-controlled parameters.
NUM_SELECTED = 5

def create_boids(position):
    boids = []
    # Create the first NUM_SELECTED boids as selected.
    for i in range(NUM_SELECTED):
        boids.append(HeteroBoid(position, selected=True))
    # Create the remaining boids with heterogeneous parameters.
    for _ in range(config.NUM_BOIDS - NUM_SELECTED):
        boids.append(HeteroBoid(position))
    return boids

def run_simulation():
    # Start with boids at the window center.
    boids = create_boids((config.WIDTH // 2, config.HEIGHT // 2))
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Process slider events.
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (speed_slider.collidepoint(event.pos) or
                    alignment_slider.collidepoint(event.pos) or
                    cohesion_slider.collidepoint(event.pos) or
                    separation_slider.collidepoint(event.pos) or
                    neighbor_radius_slider.collidepoint(event.pos) or
                    separation_radius_slider.collidepoint(event.pos)):
                    handle_slider_events(event.pos)
                    continue
                # Allow repositioning: click to reposition all boids.
                boids = create_boids(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        draw_sliders()
        if walls.walls_visible:
            draw_walls(walls.wall_positions)
        for boid in boids:
            boid.update(boids)
            # Draw selected boids in red, others in yellow.
            color = (255, 0, 0) if boid.selected else (255, 255, 0)
            pygame.draw.circle(screen, color, boid.position.astype(int), 5)

        draw_translucent_text("Press 'Esc' to exit", (10, 10), (255, 255, 255), 128)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    return boids

def plot_aggregate(boids):
    # Compute the overall group centroid.
    positions = np.array([boid.position for boid in boids])
    group_centroid = np.mean(positions, axis=0)
    # For each boid, compute the distance from the group centroid.
    distances = np.linalg.norm(positions - group_centroid, axis=1)
    # Gather each boid's neighbor radius.
    neighbor_radii = []
    for boid in boids:
        # Selected boids use the global config value.
        if boid.selected:
            neighbor_radii.append(config.NEIGHBOR_RADIUS)
        else:
            neighbor_radii.append(boid.neighbor_radius)

    # Compute Spearman correlation between neighbor_radius and distance.
    corr, p_val = spearmanr(neighbor_radii, distances)
    print("Spearman correlation (neighbor radius vs. distance): {:.3f} (p={:.3f})".format(corr, p_val))
    
    # Create scatter plot.
    plt.figure(figsize=(8, 6))
    plt.scatter(neighbor_radii, distances, c='blue', alpha=0.6)
    plt.xlabel("Neighbor Radius")
    plt.ylabel("Distance from Group Centroid")
    plt.title("Relationship between Neighbor Radius and Distance from Centroid")
    plt.grid(True)
    plt.text(0.05, 0.95,
             f"Spearman r = {corr:.3f}\np = {p_val:.3f}",
             transform=plt.gca().transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    plt.show()

if __name__ == '__main__':
    boids = run_simulation()
    plot_aggregate(boids)
