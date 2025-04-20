import pygame
import config
from boids import Boid
from directed_boids import DirectedBoid
from viz import create_boids, draw_translucent_text, draw_walls, screen, clock
import walls
from number_inputs import draw_controllers, handle_controller_event, update_parameters
import numpy as np

def menu():
    font = pygame.font.SysFont(None, 55)
    small_font = pygame.font.SysFont(None, 30)

    while True:
        screen.fill((0, 0, 0))
        texts = [
            font.render("Choose Flocking Mode", True, (255, 255, 255)),
            font.render("Press 1 for Basic Boids", True, (255, 255, 255)),
            font.render("Press 2 for Directed Boids", True, (255, 255, 255)),
            font.render("Press 3 for Heterogeneous Directed Boids", True, (255, 255, 255)),
            small_font.render(f"Walls: {'Visible' if walls.walls_visible else 'Hidden'} (Press W)", True, (255, 255, 255)),
            font.render("Press ESC/Q to Exit", True, (255, 255, 255))
        ]

        y_pos = config.HEIGHT // 2 - 100
        for text in texts:
            screen.blit(text, (config.WIDTH/2 - text.get_width()//2, y_pos))
            y_pos += 50 if text == texts[-2] else 40

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    run_simulation()
                elif event.key == pygame.K_2:
                    run_simulation(use_directed_boids=True)
                elif event.key == pygame.K_3:
                    run_simulation(use_collective_memory=True)
                elif event.key == pygame.K_w:
                    walls.walls_visible = not walls.walls_visible
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    return

def run_simulation(use_directed_boids=False, use_collective_memory=False):
    global boids
    start_position = (config.WIDTH // 2, config.HEIGHT // 2)
    goal_position = (config.WIDTH // 2, config.HEIGHT // 2)
    boids = create_boids(use_directed_boids, start_position, goal_position, use_collective_memory)
    
    # When using heterogeneous directed boids mode, flag 10% as selected.
    if use_collective_memory:
        num_selected = max(1, int(0.1 * len(boids)))
        selected_indices = np.random.choice(len(boids), num_selected, replace=False)
        for idx in selected_indices:
            boids[idx].selected = True

    running = True
    while running:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Process controller events.
            handle_controller_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If click is in control panel (to right of simulation area), do nothing more.
                if event.pos[0] >= config.WIDTH:
                    continue
                # Otherwise, if in simulation area and in directed mode, update goal.
                if use_directed_boids or use_collective_memory:
                    goal_position = event.pos
                    for boid in boids:
                        boid.goal = goal_position
                else:
                    start_position = event.pos
                    boids = create_boids(False, start_position)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu()
                    return

        update_parameters()
        # Draw control panel separately.
        draw_controllers(screen)
        if walls.walls_visible:
            draw_walls(walls.wall_positions)
            
        for boid in boids:
            boid.update(boids)
            color = (255, 0, 0) if hasattr(boid, 'selected') and boid.selected else (255, 255, 0)
            pygame.draw.circle(screen, color, boid.position.astype(int), 5)

        draw_translucent_text("Press 'Esc' to go back", (10, 10), (255, 255, 255), 128)
        pygame.display.flip()
        clock.tick(60)

menu()
pygame.quit()
