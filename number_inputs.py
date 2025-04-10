import pygame
import config

if not pygame.font.get_init():
    pygame.font.init()

class NumberController:
    def __init__(self, x, y, label, initial_value, min_val, max_val, step):
        self.x = x
        self.y = y
        self.label = label
        self.value = initial_value
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.font = pygame.font.SysFont(None, 24)
        self.minus_rect = pygame.Rect(x, y, 20, 20)
        self.plus_rect = pygame.Rect(x + 100 - 20, y, 20, 20)
        self.value_rect = pygame.Rect(x + 25, y, 50, 20)

    def draw(self, surface):
        label_surf = self.font.render(self.label, True, (255, 255, 255))
        surface.blit(label_surf, (self.x, self.y - 25))
        pygame.draw.rect(surface, (200, 0, 0), self.minus_rect)
        minus_text = self.font.render("-", True, (255, 255, 255))
        surface.blit(minus_text, (self.minus_rect.x + 5, self.minus_rect.y))
        pygame.draw.rect(surface, (0, 200, 0), self.plus_rect)
        plus_text = self.font.render("+", True, (255, 255, 255))
        surface.blit(plus_text, (self.plus_rect.x + 3, self.plus_rect.y))
        pygame.draw.rect(surface, (50, 50, 50), self.value_rect)
        value_text = self.font.render(f"{self.value:.2f}", True, (255, 255, 255))
        surface.blit(value_text, (self.value_rect.x + 5, self.value_rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.minus_rect.collidepoint(event.pos):
                self.value = max(self.min_val, self.value - self.step)
            elif self.plus_rect.collidepoint(event.pos):
                self.value = min(self.max_val, self.value + self.step)

# Global parameter dictionaries used by the boids.
selected_params = {
    "MAX_SPEED":  config.MAX_SPEED,
    "NEIGHBOR_RADIUS":  config.NEIGHBOR_RADIUS,
    "SEPARATION_RADIUS": config.SEPARATION_RADIUS,
    "ALIGNMENT_WEIGHT": config.ALIGNMENT_WEIGHT,
    "COHESION_WEIGHT": config.COHESION_WEIGHT,
    "SEPARATION_WEIGHT": config.SEPARATION_WEIGHT
}

nonselected_params = {
    "MAX_SPEED":  config.MAX_SPEED,
    "NEIGHBOR_RADIUS":  config.NEIGHBOR_RADIUS,
    "SEPARATION_RADIUS": config.SEPARATION_RADIUS,
    "ALIGNMENT_WEIGHT": config.ALIGNMENT_WEIGHT,
    "COHESION_WEIGHT": config.COHESION_WEIGHT,
    "SEPARATION_WEIGHT": config.SEPARATION_WEIGHT
}

selected_controllers = {}
nonselected_controllers = {}

# Define the control panel offset (to the right of simulation)
control_panel_offset = config.WIDTH
x_selected = control_panel_offset + 20
x_nonselected = control_panel_offset + 130
y_start = 50
y_gap = 40

params_list = [
    ("MAX_SPEED", config.MAX_SPEED, 0.5, 10, 0.5),
    ("NEIGHBOR_RADIUS", config.NEIGHBOR_RADIUS, 10, 200, 5),
    ("SEPARATION_RADIUS", config.SEPARATION_RADIUS, 5, 100, 2),
    ("ALIGNMENT_WEIGHT", config.ALIGNMENT_WEIGHT, 0.01, 1, 0.01),
    ("COHESION_WEIGHT", config.COHESION_WEIGHT, 0.001, 0.1, 0.001),
    ("SEPARATION_WEIGHT", config.SEPARATION_WEIGHT, 0.01, 1, 0.01)
]

for i, (name, init_val, min_val, max_val, step) in enumerate(params_list):
    y = y_start + i * y_gap
    selected_controllers[name] = NumberController(x_selected, y, name, init_val, min_val, max_val, step)
    nonselected_controllers[name] = NumberController(x_nonselected, y, name, init_val, min_val, max_val, step)

def draw_controllers(surface):
    # Draw header labels for each column.
    header_font = pygame.font.SysFont(None, 28)
    header_selected = header_font.render("Selected Boids", True, (255, 255, 255))
    header_nonselected = header_font.render("Other Boids", True, (255, 255, 255))
    surface.blit(header_selected, (x_selected, y_start - 40))
    surface.blit(header_nonselected, (x_nonselected, y_start - 40))
    # Draw each controller.
    for controller in selected_controllers.values():
        controller.draw(surface)
    for controller in nonselected_controllers.values():
        controller.draw(surface)

def handle_controller_event(event):
    for controller in selected_controllers.values():
        controller.handle_event(event)
    for controller in nonselected_controllers.values():
        controller.handle_event(event)

def update_parameters():
    global selected_params, nonselected_params
    for name, controller in selected_controllers.items():
        selected_params[name] = controller.value
    for name, controller in nonselected_controllers.items():
        nonselected_params[name] = controller.value
