import pygame
import config
from viz import screen

slider_width = 200
slider_height = 10
slider_spacing = 20

# Add new sliders for radius controls
speed_slider = pygame.Rect(
    config.WIDTH - slider_width - 20,
    config.HEIGHT - (slider_height + slider_spacing) * 6,  # Moved up to make room
    slider_width,
    slider_height
)

alignment_slider = pygame.Rect(
    config.WIDTH - slider_width - 20,
    config.HEIGHT - (slider_height + slider_spacing) * 5,
    slider_width,
    slider_height
)

cohesion_slider = pygame.Rect(
    config.WIDTH - slider_width - 20,
    config.HEIGHT - (slider_height + slider_spacing) * 4,
    slider_width,
    slider_height
)

separation_slider = pygame.Rect(
    config.WIDTH - slider_width - 20,
    config.HEIGHT - (slider_height + slider_spacing) * 3,
    slider_width,
    slider_height
)

# New sliders for radius controls
neighbor_radius_slider = pygame.Rect(
    config.WIDTH - slider_width - 20,
    config.HEIGHT - (slider_height + slider_spacing) * 2,
    slider_width,
    slider_height
)

separation_radius_slider = pygame.Rect(
    config.WIDTH - slider_width - 20,
    config.HEIGHT - (slider_height + slider_spacing) * 1,
    slider_width,
    slider_height
)

def draw_sliders():
    slider_surface = pygame.Surface((slider_width, slider_height))
    slider_surface.fill((255, 255, 255))
    slider_surface.set_alpha(128)

    for slider in [speed_slider, alignment_slider, cohesion_slider, separation_slider, 
                  neighbor_radius_slider, separation_radius_slider]:
        screen.blit(slider_surface, (slider.x, slider.y))

    handle_colors = [
        ((255, 165, 0), speed_slider, (config.MAX_SPEED - 1) / 9),
        ((255, 0, 0), alignment_slider, config.ALIGNMENT_WEIGHT),
        ((0, 255, 0), cohesion_slider, config.COHESION_WEIGHT),
        ((0, 0, 255), separation_slider, config.SEPARATION_WEIGHT),
        ((255, 192, 203), neighbor_radius_slider, config.NEIGHBOR_RADIUS / 100),  # Pink
        ((147, 112, 219), separation_radius_slider, config.SEPARATION_RADIUS / 40)  # Purple
    ]

    for color, slider, value in handle_colors:
        handle_x = slider.x + value * slider_width
        pygame.draw.rect(screen, color, (handle_x, slider.y, 10, 10))

    font = pygame.font.SysFont(None, 24)
    labels = [
        ("Max Speed", speed_slider),
        ("Alignment", alignment_slider),
        ("Cohesion", cohesion_slider),
        ("Separation", separation_slider),
        ("Neighbor Radius", neighbor_radius_slider),
        ("Separation Radius", separation_radius_slider)
    ]
    for text, slider in labels:
        label = font.render(text, True, (255, 255, 255))
        screen.blit(label, (slider.x + (slider_width // 2 - label.get_width() // 2), slider.y - 20))

def handle_slider_events(pos):
    if speed_slider.collidepoint(pos):
        config.MAX_SPEED = 1 + ((pos[0] - speed_slider.x) / slider_width) * 9
    elif alignment_slider.collidepoint(pos):
        config.ALIGNMENT_WEIGHT = (pos[0] - alignment_slider.x) / 200
    elif cohesion_slider.collidepoint(pos):
        config.COHESION_WEIGHT = (pos[0] - cohesion_slider.x) / 200
    elif separation_slider.collidepoint(pos):
        config.SEPARATION_WEIGHT = (pos[0] - separation_slider.x) / 200
    elif neighbor_radius_slider.collidepoint(pos):
        config.NEIGHBOR_RADIUS = ((pos[0] - neighbor_radius_slider.x) / slider_width) * 100
    elif separation_radius_slider.collidepoint(pos):
        config.SEPARATION_RADIUS = ((pos[0] - separation_radius_slider.x) / slider_width) * 40
