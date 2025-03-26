import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random

# Simulation parameters
NUM_BOIDS = 50
MAX_SPEED = 0.02
NEIGHBOR_RADIUS = 2.0
SEPARATION_RADIUS = 0.5
CUBE_SIZE = 8.0

# Boid weights
ALIGNMENT_WEIGHT = 0.100
COHESION_WEIGHT = 0.010
SEPARATION_WEIGHT = 0.010
PURSUIT_WEIGHT = 0.05
EVASION_WEIGHT = 0.1

# Leader/Evade parameters
LEADER_SPEED = 0.02
EVADE_SPEED = 0.015

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.color = color
        self.handle_width = 10
        self.handle_height = 20
        self.dragging = False
        
    def draw(self, surface):
        slider_surface = pygame.Surface((self.rect.width, self.rect.height))
        slider_surface.fill((255, 255, 255))
        slider_surface.set_alpha(128)
        surface.blit(slider_surface, (self.rect.x, self.rect.y))
        
        handle_x = self.rect.x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * self.rect.width
        pygame.draw.rect(surface, self.color, (handle_x - self.handle_width//2, self.rect.y - 5, 
                                               self.handle_width, self.handle_height))
        
        font = pygame.font.SysFont(None, 24)
        label_text = font.render(f"{self.label}: {self.value:.3f}", True, (255, 255, 255))
        surface.blit(label_text, (self.rect.x, self.rect.y - 25))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_x = self.rect.x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * self.rect.width
            handle_rect = pygame.Rect(handle_x - self.handle_width//2, self.rect.y - 5, 
                                     self.handle_width, self.handle_height)
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_ratio = (event.pos[0] - self.rect.x) / self.rect.width
            pos_ratio = max(0, min(1, pos_ratio))
            self.value = self.min_val + pos_ratio * (self.max_val - self.min_val)
            return True
            
        return False

class Boid:
    def __init__(self):
        self.position = np.random.uniform(-CUBE_SIZE/2, CUBE_SIZE/2, 3)
        direction = np.random.randn(3)
        self.velocity = direction / np.linalg.norm(direction) * MAX_SPEED
        self.color = (1, 1, 0)  # Yellow color for regular boids

    def update(self, boids, leader=None, evade=None):
        acceleration = self.flock(boids, leader, evade)
        self.velocity += acceleration
        self.velocity = self.limit_speed(self.velocity)
        self.position += self.velocity
        self.wrap_position()

    def limit_speed(self, vector):
        speed = np.linalg.norm(vector)
        if speed > MAX_SPEED:
            return (vector / speed) * MAX_SPEED
        return vector

    def wrap_position(self):
        for i in range(3):
            if self.position[i] > CUBE_SIZE / 2:
                self.position[i] -= CUBE_SIZE
            elif self.position[i] < -CUBE_SIZE / 2:
                self.position[i] += CUBE_SIZE

    def flock(self, boids, leader, evade):
        alignment = np.zeros(3)
        cohesion = np.zeros(3)
        separation = np.zeros(3)
        total = 0

        # Regular boid interactions
        for other in boids:
            if other == self:
                continue
            distance = np.linalg.norm(other.position - self.position)

            if distance < NEIGHBOR_RADIUS:
                alignment += other.velocity
                cohesion += other.position
                total += 1

            if distance < SEPARATION_RADIUS and distance > 0:
                separation -= (other.position - self.position) / distance

        # Leader interaction
        leader_influence = np.zeros(3)
        if leader and leader.active:
            leader_offset = leader.position - self.position
            distance_to_leader = np.linalg.norm(leader_offset)
            if distance_to_leader < NEIGHBOR_RADIUS:
                leader_influence = leader_offset / distance_to_leader * PURSUIT_WEIGHT

        # Evade interaction
        evade_influence = np.zeros(3)
        if evade and evade.active:
            evade_offset = evade.position - self.position
            distance_to_evade = np.linalg.norm(evade_offset)
            if distance_to_evade < NEIGHBOR_RADIUS * 1.5:
                evade_influence = -evade_offset / distance_to_evade * EVASION_WEIGHT

        if total > 0:
            alignment /= total
            alignment *= ALIGNMENT_WEIGHT

            cohesion /= total
            cohesion -= self.position
            cohesion *= COHESION_WEIGHT

        separation *= SEPARATION_WEIGHT

        return alignment + cohesion + separation + leader_influence + evade_influence

class LeaderBoid(Boid):
    def __init__(self):
        super().__init__()
        self.color = (0.0, 1.0, 0.0)  # Green color
        self.path_type = "torus"
        self.t = 0
        self.trajectory = []
        self.trajectory_max_length = 300
        self.straight_start = np.array([-CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2])
        self.straight_end = np.array([CUBE_SIZE/2, CUBE_SIZE/2, CUBE_SIZE/2])
        self.straight_direction = self.straight_end - self.straight_start
        self.straight_direction /= np.linalg.norm(self.straight_direction)
        self.active = True

    def update(self):
        self.t += LEADER_SPEED
        if self.path_type == "torus":
            self.position = np.array([
                np.sin(self.t) * CUBE_SIZE / 3,
                np.cos(self.t) * CUBE_SIZE / 3,
                np.sin(2 * self.t) * CUBE_SIZE / 3
            ])
        elif self.path_type == "straight":
            self.position += self.straight_direction * LEADER_SPEED
            if np.any(self.position > CUBE_SIZE/2) or np.any(self.position < -CUBE_SIZE/2):
                self.position = self.straight_start.copy()

        self.velocity = self.position - self.trajectory[-1] if self.trajectory else np.zeros(3)
        self.velocity = self.limit_speed(self.velocity)
        
        self.trajectory.append(self.position.copy())
        if len(self.trajectory) > self.trajectory_max_length:
            self.trajectory.pop(0)

    def toggle_path(self):
        self.path_type = "straight" if self.path_type == "torus" else "torus"
        self.t = 0
        if self.path_type == "straight":
            self.position = self.straight_start.copy()

class EvadeBoid(Boid):
    def __init__(self):
        super().__init__()
        self.color = (1.0, 0, 0.0)  # Red color
        self.path_type = "center"
        self.t = 0
        self.trajectory = []
        self.trajectory_max_length = 300
        self.active = True

    def update(self):
        self.t += EVADE_SPEED
        if self.path_type == "center":
            self.position = np.array([0.0, 0.0, 0.0])
        elif self.path_type == "torus":
            self.position = np.array([
                np.sin(self.t) * CUBE_SIZE / 2,
                np.cos(self.t) * CUBE_SIZE / 2,
                np.sin(2 * self.t) * CUBE_SIZE / 2
            ])

        self.velocity = self.position - self.trajectory[-1] if self.trajectory else np.zeros(3)
        self.velocity = self.limit_speed(self.velocity)
        
        self.trajectory.append(self.position.copy())
        if len(self.trajectory) > self.trajectory_max_length:
            self.trajectory.pop(0)

    def toggle_path(self):
        self.path_type = "torus" if self.path_type == "center" else "center"
        self.t = 0

def draw_boid(boid):
    sphere = gluNewQuadric()
    glPushMatrix()
    glTranslatef(*boid.position)
    glColor3f(*boid.color)
    gluSphere(sphere, 0.1, 10, 10)
    glPopMatrix()

def draw_cube():
    glColor4f(1.0, 1.0, 1.0, 0.5)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vertices = [
        [-CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2],
        [CUBE_SIZE/2, -CUBE_SIZE/2, -CUBE_SIZE/2],
        [CUBE_SIZE/2, CUBE_SIZE/2, -CUBE_SIZE/2],
        [-CUBE_SIZE/2, CUBE_SIZE/2, -CUBE_SIZE/2],
        [-CUBE_SIZE/2, -CUBE_SIZE/2, CUBE_SIZE/2],
        [CUBE_SIZE/2, -CUBE_SIZE/2, CUBE_SIZE/2],
        [CUBE_SIZE/2, CUBE_SIZE/2, CUBE_SIZE/2],
        [-CUBE_SIZE/2, CUBE_SIZE/2, CUBE_SIZE/2]
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

def draw_trajectory(trajectory, color):
    glColor3f(*color)
    glBegin(GL_POINTS)
    for i, pos in enumerate(trajectory):
        if i % 2 == 0:
            glVertex3fv(pos)
    glEnd()

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, toggle_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.toggle_color = toggle_color
        self.toggled = False
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.toggle_color if self.toggled else self.color, self.rect)
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.toggled = not self.toggled
                return True
        return False

def main():
    global MAX_SPEED, ALIGNMENT_WEIGHT, COHESION_WEIGHT, SEPARATION_WEIGHT, NEIGHBOR_RADIUS, SEPARATION_RADIUS
    global PURSUIT_WEIGHT, EVASION_WEIGHT, LEADER_SPEED, EVADE_SPEED
    
    pygame.init()
    display_width, display_height = 1080, 720
    display = (display_width, display_height)
    screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption("3D Boids Simulation with Leader & Evade")

    ui_surface = pygame.Surface(display, pygame.SRCALPHA)
    
    slider_width = 200
    slider_height = 10
    slider_spacing = 40
    slider_x = display_width - slider_width - 20
    
    sliders = [
        Slider(slider_x, display_height - slider_spacing * 9, slider_width, slider_height, 
               0.001, 0.05, MAX_SPEED, "Max Speed", (255, 165, 0)),
        Slider(slider_x, display_height - slider_spacing * 8, slider_width, slider_height, 
               0.001, 0.2, ALIGNMENT_WEIGHT, "Alignment", (255, 0, 0)),
        Slider(slider_x, display_height - slider_spacing * 7, slider_width, slider_height, 
               0.001, 0.1, COHESION_WEIGHT, "Cohesion", (0, 255, 0)),
        Slider(slider_x, display_height - slider_spacing * 6, slider_width, slider_height, 
               0.001, 0.2, SEPARATION_WEIGHT, "Separation", (0, 0, 255)),
        Slider(slider_x, display_height - slider_spacing * 5, slider_width, slider_height, 
               0.0, 0.3, PURSUIT_WEIGHT, "Pursuit", (255, 192, 203)),
        Slider(slider_x, display_height - slider_spacing * 4, slider_width, slider_height, 
               0.0, 0.3, EVASION_WEIGHT, "Evasion", (147, 112, 219)),
        Slider(slider_x, display_height - slider_spacing * 3, slider_width, slider_height, 
               0.001, 0.05, LEADER_SPEED, "Leader Speed", (255, 0, 0)),
        Slider(slider_x, display_height - slider_spacing * 2, slider_width, slider_height, 
               0.001, 0.05, EVADE_SPEED, "Evade Speed", (147, 112, 219)),
        Slider(slider_x, display_height - slider_spacing * 1, slider_width, slider_height, 
               0.1, 3.0, NEIGHBOR_RADIUS, "Neighbor Radius", (255, 192, 203)),
    ]

    leader_button = Button(10, 10, 120, 30, "Leader: ON", (0, 255, 0), (0, 0, 0), (255, 0, 0))
    leader_path_button = Button(140, 10, 120, 30, "Path: O", (255, 165, 0), (0, 0, 0), (255, 165, 0))
    evade_button = Button(270, 10, 140, 30, "Evade: ON", (0, 255, 0), (0, 0, 0), (255, 0, 0))
    evade_path_button = Button(420, 10, 120, 30, "Path: .", (255, 165, 0), (0, 0, 0), (255, 165, 0))

    gluPerspective(45, display[0]/display[1], 0.1, 50.0)
    glTranslatef(0.0, 0.0, -15)

    boids = [Boid() for _ in range(NUM_BOIDS)]
    leader = LeaderBoid()
    evade = EvadeBoid()
    leader_active = True
    evade_active = True

    mouse_pressed = False
    last_mouse_pos = None
    dragging_slider = False

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    help_text = font.render("Drag mouse to rotate view | Adjust sliders to change parameters", True, (255, 255, 255))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
            slider_changed = False
            for slider in sliders:
                if slider.handle_event(event):
                    slider_changed = True
                    dragging_slider = True
                    
                    MAX_SPEED = sliders[0].value
                    ALIGNMENT_WEIGHT = sliders[1].value
                    COHESION_WEIGHT = sliders[2].value
                    SEPARATION_WEIGHT = sliders[3].value
                    PURSUIT_WEIGHT = sliders[4].value
                    EVASION_WEIGHT = sliders[5].value
                    LEADER_SPEED = sliders[6].value
                    EVADE_SPEED = sliders[7].value
                    NEIGHBOR_RADIUS = sliders[8].value
                    
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False
                
            if leader_button.handle_event(event):
                leader_active = not leader_active
                leader_button.text = "Leader: ON" if leader_active else "Leader: OFF"
                leader.active = leader_active
                
            if leader_path_button.handle_event(event):
                leader.toggle_path()
                leader_path_button.text = "Path: |" if leader.path_type == "straight" else "Path: O"
                
            if evade_button.handle_event(event):
                evade_active = not evade_active
                evade_button.text = "Evade: ON" if evade_active else "Evade: OFF"
                evade.active = evade_active

            if evade_path_button.handle_event(event):
                evade.toggle_path()
                evade_path_button.text = "Path: O" if evade.path_type == "torus" else "Path: ."

            if not dragging_slider:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pressed = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_pressed = False

        if mouse_pressed and last_mouse_pos is not None and not dragging_slider:
            current_mouse_pos = pygame.mouse.get_pos()
            dx = current_mouse_pos[0] - last_mouse_pos[0]
            dy = current_mouse_pos[1] - last_mouse_pos[1]
            last_mouse_pos = current_mouse_pos

            glRotatef(dx * 0.1, 0.0, 1.0, 0.0)
            glRotatef(dy * -0.1, 1.0, 0.0, 0.0)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        ui_surface.fill((0, 0, 0, 0))
        
        glEnable(GL_DEPTH_TEST)
        draw_cube()

        if leader_active:
            leader.update()
            draw_boid(leader)
            draw_trajectory(leader.trajectory, (0.0, 1.0, 0.0)) # Green

        if evade_active:
            evade.update()
            draw_boid(evade)
            draw_trajectory(evade.trajectory, (1.0, 0.0, 0.0)) # Red

        for boid in boids:
            boid.update(boids, leader if leader_active else None, evade if evade_active else None)
            draw_boid(boid)

        for slider in sliders:
            slider.draw(ui_surface)
            
        leader_button.draw(ui_surface)
        leader_path_button.draw(ui_surface)
        evade_button.draw(ui_surface)
        evade_path_button.draw(ui_surface)

        ui_surface.blit(help_text, (10, 50))
        
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, display_width, display_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        ui_texture = pygame.image.tostring(ui_surface, "RGBA", True)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDrawPixels(display_width, display_height, GL_RGBA, GL_UNSIGNED_BYTE, ui_texture)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
