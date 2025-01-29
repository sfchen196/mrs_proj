import pygame
import config
from boids import Boid
from s_boids import DirectedBoid
from viz import create_boids, draw_translucent_text, draw_walls, screen, clock
from walls import walls_visible, wall_positions
from sliders import speed_slider, alignment_slider, cohesion_slider, separation_slider, neighbor_radius_slider, separation_radius_slider, draw_sliders, handle_slider_events

def menu():
    global walls_visible

    font = pygame.font.SysFont(None, 55)
    small_font = pygame.font.SysFont(None, 30)

    while True:
        screen.fill((0, 0, 0))
        texts = [
            font.render("Choose Flocking Mode", True, (255, 255, 255)),
            font.render("Press 1 for Basic Boids", True, (255, 255, 255)),
            font.render("Press 2 for Directed Boids", True, (255, 255, 255)),
            font.render("Press 3 for Collective Memory", True, (255, 255, 255)),
            small_font.render(f"Walls: {'Visible' if walls_visible else 'Hidden'} (Press W)", True, (255, 255, 255)),
            font.render("Press ESC/Q to Exit", True, (255, 255, 255))
        ]

        y_pos = config.HEIGHT // 2 - 100
        for text in texts:
            screen.blit(text, (config.WIDTH // 2 - text.get_width() // 2, y_pos))
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
                    walls_visible = not walls_visible
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    return

def run_simulation(use_directed_boids=False, use_collective_memory=False):
    global boids
    start_position = (config.WIDTH // 2, config.HEIGHT // 2)
    goal_position = (config.WIDTH // 2, config.HEIGHT // 2)
    boids = create_boids(use_directed_boids, start_position, goal_position, use_collective_memory)

    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check whether the click is on a slider
                if (speed_slider.collidepoint(event.pos) or
                    alignment_slider.collidepoint(event.pos) or
                    cohesion_slider.collidepoint(event.pos) or
                    separation_slider.collidepoint(event.pos) or
                    neighbor_radius_slider.collidepoint(event.pos) or
                    separation_radius_slider.collidepoint(event.pos)):
                    handle_slider_events(event.pos)
                    continue

                # Otherwise set goal/start positions based on boid type
                if use_directed_boids:
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

        draw_sliders()

        if walls_visible:
            draw_walls(wall_positions)

        for boid in boids:
            boid.update(boids)
            pygame.draw.circle(screen, (255, 255, 0), boid.position.astype(int), 5)

        draw_translucent_text("Press 'Esc' to go back", (10, 10), (255, 255, 255), 128)

        pygame.display.flip()
        clock.tick(60)

menu()
pygame.quit()
