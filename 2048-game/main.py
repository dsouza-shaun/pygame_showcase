import pygame
import random
import sys

# --- Configuration ---
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
GRID_SIZE = 4
TILE_SIZE = 100
TILE_MARGIN = 10
HEADER_HEIGHT = 100

# Colors
BACKGROUND_COLOR = (187, 173, 160)
GRID_BG_COLOR = (205, 193, 180)
TEXT_COLOR_DARK = (119, 110, 101)
TEXT_COLOR_LIGHT = (249, 246, 242)

# Color palette extending beyond 2048
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50),
    8192: (60, 58, 50),
}

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2048 Game")

# Fonts
try:
    font_score = pygame.font.SysFont("arial", 24, bold=True)
    font_large = pygame.font.SysFont("arial", 48, bold=True)
    font_base = pygame.font.SysFont("arial", 40, bold=True)
except:
    font_score = pygame.font.Font(None, 24)
    font_large = pygame.font.Font(None, 48)
    font_base = pygame.font.Font(None, 40)

class Game2048:
    def __init__(self):
        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.won = False
        self.keep_playing = False
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.grid[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.grid[r][c] = 4 if random.random() > 0.9 else 2

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score

    # --- Movement Logic ---
    def stack(self, row):
        """Slide all non-zero tiles to the left"""
        new_row = [i for i in row if i != 0]
        new_row += [0] * (GRID_SIZE - len(new_row))
        return new_row

    def combine(self, row):
        """Combine adjacent equal tiles"""
        for i in range(GRID_SIZE - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                row[i + 1] = 0
                self.score += row[i]
                # Check win condition only once
                if row[i] == 2048 and not self.won and not self.keep_playing:
                    self.won = True
        return row

    def move_left(self):
        moved = False
        for r in range(GRID_SIZE):
            original_row = self.grid[r].copy()
            new_row = self.stack(self.grid[r])
            new_row = self.combine(new_row)
            new_row = self.stack(new_row)
            self.grid[r] = new_row
            if original_row != new_row:
                moved = True
        if moved:
            self.update_high_score()
        return moved

    def move_right(self):
        moved = False
        for r in range(GRID_SIZE):
            original_row = self.grid[r].copy()
            # Reverse, process left logic, reverse back
            new_row = self.grid[r][::-1]
            new_row = self.stack(new_row)
            new_row = self.combine(new_row)
            new_row = self.stack(new_row)
            self.grid[r] = new_row[::-1]
            if original_row != self.grid[r]:
                moved = True
        if moved:
            self.update_high_score()
        return moved

    def move_up(self):
        moved = False
        for c in range(GRID_SIZE):
            original_col = [self.grid[r][c] for r in range(GRID_SIZE)]
            # Treat column as a row
            col_data = [self.grid[r][c] for r in range(GRID_SIZE)]
            col_data = self.stack(col_data)
            col_data = self.combine(col_data)
            col_data = self.stack(col_data)

            new_col = col_data
            for r in range(GRID_SIZE):
                self.grid[r][c] = new_col[r]

            if original_col != new_col:
                moved = True
        if moved:
            self.update_high_score()
        return moved

    def move_down(self):
        moved = False
        for c in range(GRID_SIZE):
            original_col = [self.grid[r][c] for r in range(GRID_SIZE)]
            col_data = [self.grid[r][c] for r in range(GRID_SIZE)][::-1]
            col_data = self.stack(col_data)
            col_data = self.combine(col_data)
            col_data = self.stack(col_data)
            new_col = col_data[::-1]

            for r in range(GRID_SIZE):
                self.grid[r][c] = new_col[r]

            if original_col != new_col:
                moved = True
        if moved:
            self.update_high_score()
        return moved

    def check_state(self):
        # If not game over yet
        if not self.game_over:
            # Check for empty cells
            if any(0 in row for row in self.grid):
                return

            # Check for possible horizontal merges
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE - 1):
                    if self.grid[r][c] == self.grid[r][c + 1]:
                        return

            # Check for possible vertical merges
            for c in range(GRID_SIZE):
                for r in range(GRID_SIZE - 1):
                    if self.grid[r][c] == self.grid[r + 1][c]:
                        return

            # If no moves left
            self.game_over = True

    def reset(self):
        self.__init__()

    def draw_text_centered(self, text, font, color, center_x, center_y):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(center_x, center_y))
        screen.blit(surface, rect)

    def draw_tile(self, r, c, value):
        # Calculate position based on offset header
        x_offset = (SCREEN_WIDTH - (GRID_SIZE * TILE_SIZE + (GRID_SIZE - 1) * TILE_MARGIN)) // 2
        y_offset = HEADER_HEIGHT

        x = x_offset + c * (TILE_SIZE + TILE_MARGIN)
        y = y_offset + r * (TILE_SIZE + TILE_MARGIN)

        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        color = TILE_COLORS.get(value, (60, 58, 50))
        pygame.draw.rect(screen, color, rect, border_radius=5)

        if value != 0:
            text_color = TEXT_COLOR_DARK if value <= 4 else TEXT_COLOR_LIGHT

            # Dynamic Font Size
            font_size = 40
            if value > 100 and value < 1000:
                font_size = 35
            elif value >= 1000:
                font_size = 28

            tile_font = pygame.font.SysFont("arial", font_size, bold=True)

            text = tile_font.render(str(value), True, text_color)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    def draw(self):
        screen.fill(BACKGROUND_COLOR)

        # Draw Header Background
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HEADER_HEIGHT)
        pygame.draw.rect(screen, BACKGROUND_COLOR, header_rect)

        # Draw Title
        self.draw_text_centered("2048", font_large, TEXT_COLOR_DARK, SCREEN_WIDTH // 4, HEADER_HEIGHT // 2)

        # Draw Score Box
        score_box_x = SCREEN_WIDTH - 180
        score_rect = pygame.Rect(score_box_x, 20, 150, 60)
        pygame.draw.rect(screen, GRID_BG_COLOR, score_rect, border_radius=3)
        self.draw_text_centered("SCORE", font_score, (238, 228, 218), score_rect.centerx, score_rect.top + 15)
        self.draw_text_centered(str(self.score), font_score, TEXT_COLOR_WHITE := (255, 255, 255), score_rect.centerx, score_rect.bottom - 15)

        # Draw Grid Background
        grid_width = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * TILE_MARGIN
        grid_x = (SCREEN_WIDTH - grid_width) // 2
        grid_y = HEADER_HEIGHT
        grid_rect = pygame.Rect(grid_x, grid_y, grid_width, grid_width)
        pygame.draw.rect(screen, GRID_BG_COLOR, grid_rect, border_radius=5)

        # Draw Tiles
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.draw_tile(r, c, self.grid[r][c])

        # Draw Game Over / Win Overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180)) # Semi-transparent white
            screen.blit(overlay, (0,0))
            self.draw_text_centered("Game Over!", font_large, TEXT_COLOR_DARK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
            self.draw_text_centered("Press Enter to Restart", font_score, TEXT_COLOR_DARK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)

        elif self.won and not self.keep_playing:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((237, 194, 46, 180)) # Gold tint
            screen.blit(overlay, (0,0))
            self.draw_text_centered("You Win!", font_large, TEXT_COLOR_WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
            self.draw_text_centered("Press Enter to Continue", font_score, TEXT_COLOR_WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
            self.draw_text_centered("or R to Restart", font_score, TEXT_COLOR_WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)

def main():
    game = Game2048()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                moved = False

                if game.game_over:
                    if event.key == pygame.K_RETURN:
                        game.reset()
                elif game.won and not game.keep_playing:
                    if event.key == pygame.K_RETURN:
                        game.keep_playing = True
                        game.won = False # Disable win screen
                    elif event.key == pygame.K_r:
                        game.reset()
                else:
                    if event.key == pygame.K_LEFT:
                        moved = game.move_left()
                    elif event.key == pygame.K_RIGHT:
                        moved = game.move_right()
                    elif event.key == pygame.K_UP:
                        moved = game.move_up()
                    elif event.key == pygame.K_DOWN:
                        moved = game.move_down()

                    if moved:
                        game.add_new_tile()
                        game.check_state()

        game.draw()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()