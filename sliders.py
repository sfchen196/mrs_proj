import pygame

class Slider:
    def __init__(self, x, y, width, height, min_value, max_value, default_value):
        self.rect = pygame.Rect(x, y, width, height)
        self.background = pygame.Surface((width, height))
        self.background.fill((200, 200, 200))
        
        self.handle = pygame.Rect(x, y, 20, height)
        self.handle_dragging = False
        
        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value
        
        self.value_changed = False
        
    def draw(self, screen):
        screen.blit(self.background, self.rect)
        screen.blit(self.handle, (self.handle.x, self.handle.y))
        
        # Draw value label
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.value:.2f}", True, (0, 0, 0))
        screen.blit(text, (self.rect.right + 10, self.rect.top))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle.collidepoint(event.pos):
                self.handle_dragging = True
                self.value_changed = False
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.handle_dragging:
            # Update handle position based on mouse movement
            self.handle.x = max(self.rect.left, min(event.pos[0], self.rect.right - self.handle.width))
            
            # Calculate value based on position
            value_range = self.max_value - self.min_value
            position_range = self.rect.width - self.handle.width
            self.value = ((self.handle.x - self.rect.left) / position_range) * value_range + self.min_value
            self.value_changed = True
            
            return True
        return False
