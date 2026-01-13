import pygame

# --- INITIALIZATION ---
pygame.init()
pygame.font.init()

# --- DISPLAY CONFIGURATION ---
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600
gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Tetris')

# --- COLORS & AESTHETICS ---
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
DARK_GRAY  = (80, 80, 80)
GRAY       = (110, 110, 110)
LIGHT_GRAY = (150, 150, 150)

BORDER_COLOR = GRAY
NUM_COLOR    = WHITE
TEXT_COLOR   = GRAY

# Colors mapped to specific Tetriminos
blockColors = {
    'I': (19, 232, 232),  # Cyan
    'O': (236, 236, 14),  # Yellow
    'T': (126, 5, 126),   # Purple
    'S': (0, 128, 0),     # Green
    'Z': (236, 14, 14),   # Red
    'J': (30, 30, 201),   # Blue
    'L': (240, 110, 2)    # Orange
}

# --- FONTS ---
# Standardizing font sizes for various UI elements
SB_FONT_SIZE       = 29
FONT_SIZE_SMALL    = 17
PAUSE_FONT_SIZE    = 66
GAMEOVER_FONT_SIZE = 66
TITLE_FONT_SIZE    = 70
VERSION_FONT_SIZE  = 20

fontSB       = pygame.font.SysFont('agencyfb', SB_FONT_SIZE)
fontSmall    = pygame.font.SysFont('agencyfb', FONT_SIZE_SMALL)
fontPAUSE    = pygame.font.SysFont('agencyfb', PAUSE_FONT_SIZE)
fontGAMEOVER = pygame.font.SysFont('agencyfb', GAMEOVER_FONT_SIZE)
fontTitle    = pygame.font.SysFont('agencyfb', TITLE_FONT_SIZE)
fontVersion  = pygame.font.SysFont('agencyfb', VERSION_FONT_SIZE)

# --- GAME LOGIC CONSTANTS ---
ROW = 0
COL = 1

STARTING_LEVEL   = 0   # Starting difficulty
MOVE_PERIOD_INIT = 4   # Frames between movements when keys are held (60 FPS base)
CLEAR_ANI_PERIOD = 4   # Speed of the line-clear flash animation
SINE_ANI_PERIOD  = 120 # Duration of the pulsing/blinking menu effect

# Movement vectors (y, x)
directions = {
    'down':      (1, 0),
    'right':     (0, 1),
    'left':      (0, -1),
    'downRight': (1, 1),
    'downLeft':  (1, -1),
    'noMove':    (0, 0)
}

# --- TETRIMINO DEFINITIONS ---
pieceNames = ('I', 'O', 'T', 'S', 'Z', 'J', 'L')

# Spawn coordinates for each piece relative to its local grid
pieceDefs = {
    'I': ((1, 0), (1, 1), (1, 2), (1, 3)),
    'O': ((0, 1), (0, 2), (1, 1), (1, 2)),
    'T': ((0, 1), (1, 0), (1, 1), (1, 2)),
    'S': ((0, 1), (0, 2), (1, 0), (1, 1)),
    'Z': ((0, 0), (0, 1), (1, 1), (1, 2)),
    'J': ((0, 0), (1, 0), (1, 1), (1, 2)),
    'L': ((0, 2), (1, 0), (1, 1), (1, 2))
}

# --- LEVELING & SCORING ---
levelSpeeds = (48,43,38,33,28,23,18,13,8,6,5,5,5,4,4,4,3,3,3,2,2,2,2,2,2,2,2,2,2)
#The speed of the moving piece at each level. Level speeds are defined as levelSpeeds[level]
#Each 10 cleared lines means a level up.
#After level 29, speed is always 1. Max level is 99

baseLinePoints = (0,40,100,300,1200)
#Total score is calculated as: Score = level*baseLinePoints[clearedLineNumberAtATime] + totalDropCount
#Drop means the action the player forces the piece down instead of free fall(By key combinations: down, down-left, down-right arrows)

# Placeholders for global game objects that are instantiated in main.py
key = None
gameClock = None