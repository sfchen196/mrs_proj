import pygame
from config import WIDTH, HEIGHT, screen, clock
from boids import Boid
from s_boids import DirectedBoid
from viz import create_boids, draw_translucent_text, draw_sliders, draw_walls, handle_slider_events
from config import MAX_SPEED, ALIGNMENT_WEIGHT, COHESION_WEIGHT, SEPARATION_WEIGHT
from walls import walls_visible, wall_positions
from sliders import speed_slider, alignment_slider, cohesion_slider, separation_slider, Slider

def menu():
    global walls_visible
    font = pygame.font.SysFont(None, 55)
    small_font = pygame.font.SysFont(None, 30)
    
    while True:
        screen.fill((0,0,0))
        # Text rendering
        texts = [
            font.render("Choose Flocking Mode", True, (255,255,255)),
            font.render("Press 1 for Basic Boids", True, (255,255,255)),
            font.render("Press 2 for Directed Boids", True, (255,255,255)),
            font.render("Press 3 for Collective Memory", True, (255,255,255)),
            small_font.render(f"Walls: {'Visible' if walls_visible else 'Hidden'} (Press W)", True, (255,255,255)),
            font.render("Press ESC/Q to Exit", True, (255,255,255))
        ]
        
        # Text positioning
        y_pos = HEIGHT//2 - 100
        for text in texts:
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 50 if text == texts[-2] else 40

        pygame.display.flip()

        # Event handling (MOVED INSIDE THE MAIN LOOP)
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

# Update run_simulation
def run_simulation(use_directed_boids=False, use_collective_memory=False):
    global boids
    start_position = (WIDTH//2, HEIGHT//2)
    goal_position = (WIDTH//2, HEIGHT//2)
    boids = create_boids(use_directed_boids, start_position, goal_position, use_collective_memory)
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (speed_slider.collidepoint(event.pos) or 
                    alignment_slider.collidepoint(event.pos) or
                    cohesion_slider.collidepoint(event.pos) or
                    separation_slider.collidepoint(event.pos)):
                    handle_slider_events(event.pos)
                    continue  # Skip the rest of the MOUSEBUTTONDOWN logic if over a slider
                
                if use_directed_boids:
                    goal_position = event.pos  # Set new goal position for Directed Boids
                    for boid in boids:
                        boid.goal = goal_position  # Update each Directed Boid's goal
                else:
                    start_position = event.pos  # Set new start position for normal Boids
                    boids = create_boids(False, start_position)  # Recreate normal Boids

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Check for 'Esc' key to return to menu
                    menu()
                    return  # Exit the current simulation loop

        draw_sliders()
        
        # Draw walls only if visible
        if walls_visible:
            draw_walls(wall_positions)

        for boid in boids:
            boid.update(boids)
            pygame.draw.circle(screen, (255, 255, 0), boid.position.astype(int), 5)

        # Draw the translucent text at the top of the window
        draw_translucent_text("Press 'Esc' to go back", (10, 10), (255, 255, 255), 128)  # White text with 50% opacity

        pygame.display.flip()
        clock.tick(60)  # Limit the frame rate

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
menu()

# Create sliders
slider_max_speed = Slider(
    x=10, y=10, width=200, height=20,
    min_value=0, max_value=10, default_value=2
)

slider_alignment = Slider(
    x=10, y=40, width=200, height=20,
    min_value=0, max_value=0.1, default_value=0.01
)

slider_cohesion = Slider(
    x=10, y=70, width=200, height=20,
    min_value=0, max_value=0.001, default_value=0.001
)

slider_separation = Slider(
    x=10, y=100, width=200, height=20,
    min_value=0, max_value=0.1, default_value=0.01
)

# Create boids
boids = [Boid(400, 300) for _ in range(50)]

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Update all sliders
        slider_max_speed.handle_event(event)
        slider_alignment.handle_event(event)
        slider_cohesion.handle_event(event)
        slider_separation.handle_event(event)
    
    # Update boid parameters from sliders
    for boid in boids:
        boid.max_speed = slider_max_speed.value
        boid.alignment_weight = slider_alignment.value
        boid.cohesion_weight = slider_cohesion.value
        boid.separation_weight = slider_separation.value
    
    # Update boids
    for boid in boids:
        boid.update(boids)
    
    # Draw everything
    screen.fill((0, 0, 0))
    
    # Draw sliders
    slider_max_speed.draw(screen)
    slider_alignment.draw(screen)
    slider_cohesion.draw(screen)
    slider_separation.draw(screen)
    
    # Draw boids
    for boid in boids:
        pygame.draw.circle(screen, (255, 255, 255), 
                          (int(boid.position[0]), int(boid.position[1])), 
                          3)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()