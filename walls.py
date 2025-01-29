import pygame
from config import WIDTH, HEIGHT

# Define wall positions for screen borders and center "+"
walls_visible = False  # Initialize wall visibility
wall_positions = [
    # Borders
    pygame.Rect(0, 0, WIDTH, 10),  # Top border
    pygame.Rect(0, 0, 10, HEIGHT),  # Left border
    pygame.Rect(WIDTH - 10, 0, 10, HEIGHT),  # Right border
    pygame.Rect(0, HEIGHT - 10, WIDTH, 10),  # Bottom border
    # Plus sign
    pygame.Rect(WIDTH // 2.75 - 5, HEIGHT // 1.3 - 50, 10, 100),  # Vertical part of the "+"
    pygame.Rect(WIDTH // 2.75 - 50, HEIGHT // 1.3 - 5, 100, 10),  # Horizontal part of the "+"
    # Inverted T shape
    pygame.Rect(WIDTH - WIDTH // 6 - 5, HEIGHT - HEIGHT // 1.5 - 100, 10, 100),  # Vertical part of the "T"
    pygame.Rect(WIDTH - WIDTH // 6 - 50, HEIGHT - HEIGHT // 1.5 - 5, 100, 10),  # Horizontal part of the "T"
    # I shape
    pygame.Rect(WIDTH // 10 - 5, HEIGHT // 1.2 - 50, 10, 100),  # Vertical part of the "I"
    pygame.Rect(WIDTH // 6 - 5, HEIGHT // 3.5 - 50, 10, 100),  # Vertical part of the "I"
    pygame.Rect(WIDTH // 1.15 - 5, HEIGHT // 1.2 - 50, 10, 100),  # Vertical part of the "I"
    # L shape
    pygame.Rect(WIDTH - WIDTH // 1.4 - 5, HEIGHT - HEIGHT, 10, 100),  # Vertical part of the "L"
    pygame.Rect(WIDTH - WIDTH // 1.4 - 5, HEIGHT - HEIGHT // 1.5 - 5, 100, 10),  # Horizontal part of the "L"
    # H shape
    pygame.Rect(WIDTH // 1.65 - 50, HEIGHT // 1.75 - 50, 10, 100),  # Left vertical part of the "H"
    pygame.Rect(WIDTH // 1.65 + 40, HEIGHT // 1.75 - 50, 10, 100),  # Right vertical part of the "H"
    pygame.Rect(WIDTH // 1.65 - 50, HEIGHT // 1.75 - 5, 100, 10)  # Horizontal part of the "H"
]

