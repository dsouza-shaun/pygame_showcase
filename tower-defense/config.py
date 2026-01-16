import pygame

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
SIDEBAR_WIDTH = 220
PLAY_WIDTH = WIDTH - SIDEBAR_WIDTH
FPS = 60

# Grid settings
GRID_SIZE = 40
GRID_WIDTH = PLAY_WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
RED = (200, 50, 50)
BLUE = (50, 100, 220)
YELLOW = (230, 200, 50)
ORANGE = (255, 140, 0)
PURPLE = (150, 50, 200)
CYAN = (50, 200, 220)
BROWN = (139, 90, 43)
DARK_BROWN = (90, 60, 30)
BG_COLOR = (34, 85, 51)
SIDEBAR_BG = (40, 45, 55)
GOLD = (255, 215, 0)  # <--- Added this

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3
PAUSED = 4

# Tower Types Configuration
TOWER_TYPES = {
    'basic': {'cost': 50, 'damage': 25, 'range': 120, 'fire_rate': 1.0, 'color': BLUE,
              'projectile_speed': 8, 'description': 'Balanced tower'},
    'sniper': {'cost': 100, 'damage': 100, 'range': 250, 'fire_rate': 0.4, 'color': PURPLE,
               'projectile_speed': 20, 'description': 'Long range, high damage'},
    'splash': {'cost': 80, 'damage': 20, 'range': 100, 'fire_rate': 0.7, 'color': ORANGE,
               'projectile_speed': 6, 'splash_radius': 60, 'description': 'Area damage'},
    'slow': {'cost': 65, 'damage': 10, 'range': 110, 'fire_rate': 1.2, 'color': CYAN,
             'projectile_speed': 10, 'slow_amount': 0.5, 'description': 'Slows enemies'},
    'rapid': {'cost': 90, 'damage': 12, 'range': 100, 'fire_rate': 3.0, 'color': YELLOW,
              'projectile_speed': 12, 'description': 'Very fast firing'},
}

# Enemy Types Configuration
ENEMY_TYPES = {
    'normal': {'health': 100, 'speed': 2.0, 'reward': 15, 'color': RED, 'size': 12},
    'fast': {'health': 60, 'speed': 4.0, 'reward': 20, 'color': YELLOW, 'size': 10},
    'tank': {'health': 400, 'speed': 1.0, 'reward': 40, 'color': (100, 100, 100), 'size': 18},
    'healer': {'health': 150, 'speed': 1.8, 'reward': 35, 'color': GREEN, 'size': 14, 'heals': True},
    'boss': {'health': 2000, 'speed': 0.7, 'reward': 200, 'color': PURPLE, 'size': 28},
}

# Waypoints
PATH = [
    (-30, 280), (120, 280), (120, 80), (280, 80), (280, 400),
    (440, 400), (440, 160), (600, 160), (600, 520), (760, 520),
    (760, 280), (PLAY_WIDTH + 30, 280),
]