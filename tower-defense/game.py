import random

import pygame

import config
from enemy import Enemy
from floating_text import FloatingText
from particle import Particle
from tower import Tower
from ui import Button, draw_icon_text
from utils import distance, save_game, load_game


class Game:
    def __init__(self):
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 72)
        self.reset()
        self.setup_ui()

    def reset(self):
        self.state = config.MENU
        self.money = 250 # Increased starting money slightly for better UX
        self.lives = 20
        self.wave = 0
        self.max_waves = 25
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.floating_texts = []
        self.selected_tower_type = 'basic'
        self.selected_tower = None
        self.wave_in_progress = False
        self.enemies_to_spawn = []
        self.spawn_timer = 0
        self.path = config.PATH
        self.grid = self.create_grid()
        self.hover_pos = None
        self.score = 0
        self.game_speed = 1
        self.setup_ui()

    def setup_ui(self):
        sx = config.PLAY_WIDTH
        # Tower Select Buttons
        self.tower_buttons = []
        y = 130
        for t_type, stats in config.TOWER_TYPES.items():
            # Increased height to 70 to fit metadata
            # Tag allows us to identify which tower this button represents
            btn = Button(sx + 10, y, config.SIDEBAR_WIDTH - 20, 70,
                         "", # Empty text so we can draw custom text
                         lambda t=t_type: self.select_tower_type(t),
                         color=stats['color'],
                         tag=t_type)
            self.tower_buttons.append(btn)
            y += 75 # Increased spacing slightly

        # Control Buttons
        self.start_wave_btn = Button(sx + 10, y + 10, config.SIDEBAR_WIDTH - 20, 40, "START WAVE", self.start_wave, color=config.DARK_GREEN)

        self.speed_btn = Button(sx + 10, y + 60, 65, 30, "SPEED", self.toggle_speed, color=config.GRAY)
        self.save_btn = Button(sx + config.SIDEBAR_WIDTH - 75, y + 60, 65, 30, "SAVE", self.save_game_state, color=config.BLUE)

        # Context sensitive buttons
        self.upgrade_btn = Button(0, 0, 80, 30, "UP", lambda: self.upgrade_selected(), color=config.GREEN)
        self.sell_btn = Button(0, 0, 80, 30, "SELL", lambda: self.sell_selected(), color=config.RED)
        self.target_btn = Button(0, 0, 120, 30, "TARGET: First", self.cycle_targeting, color=config.GRAY)

    def draw_sidebar(self, screen):
        sx = config.PLAY_WIDTH
        pygame.draw.rect(screen, config.SIDEBAR_BG, (sx, 0, config.SIDEBAR_WIDTH, config.HEIGHT))
        pygame.draw.line(screen, (60, 65, 75), (sx, 0), (sx, config.HEIGHT), 3)

        y = 15
        # Stats
        stats = [
            (f"Wave: {self.wave}/{self.max_waves}", config.WHITE),
            (f"Money: ${self.money}", config.YELLOW if self.money < 50 else config.GREEN),
            (f"Lives: {self.lives}", config.RED if self.lives <= 5 else config.GREEN),
            (f"Score: {self.score}", config.CYAN),
        ]
        for text, color in stats:
            draw_icon_text(screen, text, sx + 15, y, color)
            y += 25

        pygame.draw.line(screen, config.GRAY, (sx + 10, y + 5), (config.WIDTH - 10, y + 5), 1)

        # Tower Buttons with Metadata
        for btn in self.tower_buttons:
            # Set active state based on selection
            btn.is_active = (btn.tag == self.selected_tower_type)

            # Draw the button background and border
            btn.draw(screen)

            # --- Draw Custom Metadata ---
            t_type = btn.tag
            t_stats = config.TOWER_TYPES[t_type]

            # 1. Tower Name (Top Center)
            name_surf = self.font.render(t_type.upper(), True, config.WHITE)
            name_rect = name_surf.get_rect(center=(btn.rect.centerx, btn.rect.y + 20))
            screen.blit(name_surf, name_rect)

            # 2. Cost (Middle Left)
            cost_color = config.YELLOW if self.money >= t_stats['cost'] else config.RED
            cost_surf = self.small_font.render(f"Cost: ${t_stats['cost']}", True, cost_color)
            screen.blit(cost_surf, (btn.rect.x + 10, btn.rect.y + 38))

            # 3. Damage (Middle Right)
            dmg_surf = self.small_font.render(f"Dmg: {t_stats['damage']}", True, config.WHITE)
            screen.blit(dmg_surf, (btn.rect.x + 10, btn.rect.y + 52))

            # 4. Range (Optional, can be added if space permits, strictly following your request for Dmg/Cost)

        # Controls
        self.start_wave_btn.text = "WAVE..." if self.wave_in_progress else "START WAVE"
        self.start_wave_btn.draw(screen)
        self.speed_btn.text = f"SPD {self.game_speed}X"
        self.speed_btn.draw(screen)
        self.save_btn.draw(screen)

        # Selection Info
        if self.selected_tower:
            y = config.HEIGHT - 200
            pygame.draw.rect(screen, (50, 55, 65), (sx + 5, y, config.SIDEBAR_WIDTH - 10, 195), border_radius=8)

            draw_icon_text(screen, f"{self.selected_tower.tower_type.upper()}", sx + 15, y + 8, self.selected_tower.color, 28)

            info = [
                f"Lvl: {self.selected_tower.level}/3",
                f"Dmg: {self.selected_tower.damage}",
                f"Rng: {self.selected_tower.range}",
                f"Kills: {self.selected_tower.kills}",
            ]
            for i, txt in enumerate(info):
                draw_icon_text(screen, txt, sx + 15, y + 40 + i * 22)

            # Position dynamic buttons
            self.upgrade_btn.rect.topleft = (sx + 10, y + 130)
            self.sell_btn.rect.topleft = (sx + 100, y + 130)

            if self.selected_tower.level < 3:
                self.upgrade_btn.text = f"UP ${self.selected_tower.get_upgrade_cost()}"
                self.upgrade_btn.draw(screen)
            self.sell_btn.text = f"SELL ${self.selected_tower.get_sell_value()}"
            self.sell_btn.draw(screen)

            self.target_btn.rect.topleft = (sx + 10, y + 165)
            self.target_btn.text = f"TARGET: {self.selected_tower.targeting_mode.upper()}"
            self.target_btn.draw(screen)

    def create_grid(self):
        grid = [[True for _ in range(config.GRID_WIDTH)] for _ in range(config.GRID_HEIGHT)]
        # Mark path and surrounding cells as unavailable
        for i in range(len(self.path) - 1):
            x1, y1 = self.path[i]
            x2, y2 = self.path[i + 1]
            steps = int(max(abs(x2 - x1), abs(y2 - y1)) / 5) + 1
            for j in range(steps + 1):
                t = j / steps
                px = int(x1 + (x2 - x1) * t)
                py = int(y1 + (y2 - y1) * t)
                gx, gy = px // config.GRID_SIZE, py // config.GRID_SIZE
                # Make path and neighbors unwalkable for towers
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        ngx, ngy = gx + dx, gy + dy
                        if 0 <= ngx < config.GRID_WIDTH and 0 <= ngy < config.GRID_HEIGHT:
                            grid[ngy][ngx] = False
        return grid

    # --- Actions ---
    def select_tower_type(self, t_type):
        self.selected_tower_type = t_type
        self.selected_tower = None

    def start_wave(self):
        if self.state != config.PLAYING or self.wave_in_progress:
            return

        if self.wave >= self.max_waves:
            self.state = config.VICTORY
            return

        self.wave += 1
        self.wave_in_progress = True
        self.enemies_to_spawn = []
        wave_multiplier = 1 + (self.wave - 1) * 0.1
        num_enemies = 5 + self.wave * 2

        for i in range(num_enemies):
            if self.wave >= 20 and i == 0:
                self.enemies_to_spawn.append(('boss', wave_multiplier))
            elif self.wave >= 15 and random.random() < 0.15:
                self.enemies_to_spawn.append(('healer', wave_multiplier))
            elif self.wave >= 8 and random.random() < 0.2:
                self.enemies_to_spawn.append(('tank', wave_multiplier))
            elif self.wave >= 4 and random.random() < 0.3:
                self.enemies_to_spawn.append(('fast', wave_multiplier))
            else:
                self.enemies_to_spawn.append(('normal', wave_multiplier))

        if self.wave == self.max_waves:
            self.enemies_to_spawn.append(('boss', wave_multiplier * 1.5))

        self.spawn_timer = pygame.time.get_ticks()

    def toggle_speed(self):
        self.game_speed = 2 if self.game_speed == 1 else 1

    def save_game_state(self):
        if save_game(self):
            self.floating_texts.append(FloatingText(config.PLAY_WIDTH//2, config.HEIGHT//2, "GAME SAVED", config.GREEN, 40, speed=2))

    def upgrade_selected(self):
        if self.selected_tower:
            cost = self.selected_tower.get_upgrade_cost()
            if self.money >= cost and self.selected_tower.upgrade():
                self.money -= cost

    def sell_selected(self):
        if self.selected_tower:
            self.money += self.selected_tower.get_sell_value()
            gx, gy = self.selected_tower.x // config.GRID_SIZE, self.selected_tower.y // config.GRID_SIZE
            self.grid[gy][gx] = True
            self.towers.remove(self.selected_tower)
            self.selected_tower = None

    def cycle_targeting(self):
        if self.selected_tower:
            modes = ['first', 'strong', 'weak', 'close']
            curr_idx = modes.index(self.selected_tower.targeting_mode)
            self.selected_tower.targeting_mode = modes[(curr_idx + 1) % len(modes)]
            self.target_btn.text = f"TARGET: {self.selected_tower.targeting_mode.upper()}"

    # --- Logic ---
    def spawn_enemy(self):
        if self.enemies_to_spawn and pygame.time.get_ticks() - self.spawn_timer > (600 // self.game_speed):
            enemy_type, multiplier = self.enemies_to_spawn.pop(0)
            self.enemies.append(Enemy(self.path.copy(), enemy_type, multiplier))
            self.spawn_timer = pygame.time.get_ticks()

    def place_tower(self, pos):
        gx, gy = pos[0] // config.GRID_SIZE, pos[1] // config.GRID_SIZE

        if not (0 <= gx < config.GRID_WIDTH and 0 <= gy < config.GRID_HEIGHT):
            return False
        if not self.grid[gy][gx]:
            return False

        for tower in self.towers:
            if tower.x // config.GRID_SIZE == gx and tower.y // config.GRID_SIZE == gy:
                return False

        cost = config.TOWER_TYPES[self.selected_tower_type]['cost']
        if self.money >= cost:
            self.money -= cost
            tx = gx * config.GRID_SIZE + config.GRID_SIZE // 2
            ty = gy * config.GRID_SIZE + config.GRID_SIZE // 2
            self.towers.append(Tower(tx, ty, self.selected_tower_type))

            # Placement particles
            for _ in range(10):
                self.particles.append(Particle(tx, ty, config.WHITE))
            return True
        return False

    def handle_click(self, pos, button):
        sx = config.PLAY_WIDTH

        # UI Interactions
        if pos[0] >= sx:
            # Tower buttons
            for btn in self.tower_buttons:
                if btn.rect.collidepoint(pos):
                    btn.callback()
                    return

            # Control buttons
            if self.start_wave_btn.rect.collidepoint(pos): self.start_wave_btn.callback()
            if self.speed_btn.rect.collidepoint(pos): self.speed_btn.callback()
            if self.save_btn.rect.collidepoint(pos): self.save_btn.callback()

            # Selected Tower Buttons
            if self.selected_tower:
                if self.upgrade_btn.rect.collidepoint(pos): self.upgrade_btn.callback()
                if self.sell_btn.rect.collidepoint(pos): self.sell_btn.callback()
                if self.target_btn.rect.collidepoint(pos): self.target_btn.callback()
            return

        # Game Field Interactions
        if button == 3: # Right click
            self.selected_tower = None
            return

        # Check existing towers
        clicked_tower = False
        for tower in self.towers:
            if distance(pos, (tower.x, tower.y)) < 20:
                self.selected_tower = tower
                self.selected_tower_type = None
                clicked_tower = True
                # Reset targeting button text
                self.target_btn.text = f"TARGET: {tower.targeting_mode.upper()}"
                break

        if not clicked_tower:
            self.place_tower(pos)

    def update(self):
        # Multiple updates for speed
        for _ in range(self.game_speed):
            if self.state != config.PLAYING:
                return

            current_time = pygame.time.get_ticks()
            self.spawn_enemy()

            if self.wave_in_progress and not self.enemies_to_spawn and not self.enemies:
                self.wave_in_progress = False
                self.money += 25 + self.wave * 5
                self.floating_texts.append(FloatingText(config.PLAY_WIDTH//2, 100, "WAVE COMPLETE!", config.GOLD, 40, speed=1))

            # Towers
            for tower in self.towers:
                tower.find_target(self.enemies)
                tower.shoot(current_time, self.projectiles)

            # Projectiles
            self.projectiles = [p for p in self.projectiles if p.update(self.enemies, self.particles, self.floating_texts)]

            # Enemies
            enemies_to_remove = []
            for enemy in self.enemies:
                result = enemy.update(self.enemies, self.particles, self.floating_texts)
                if result == 'dead':
                    self.money += enemy.reward
                    self.score += enemy.reward
                    self.floating_texts.append(FloatingText(enemy.x, enemy.y - 20, f"+${enemy.reward}", config.YELLOW))
                    enemies_to_remove.append(enemy)
                elif result == 'reached_end':
                    self.lives -= 1
                    enemies_to_remove.append(enemy)
                    for _ in range(5):
                        self.particles.append(Particle(config.PLAY_WIDTH, 280, config.RED, lifetime=40))
                    if self.lives <= 0:
                        self.state = config.GAME_OVER

            for e in enemies_to_remove:
                if e in self.enemies:
                    self.enemies.remove(e)

        # Particles and Floating Text (don't speed up purely visual effects to keep it smooth)
        self.particles = [p for p in self.particles if p.update()]
        self.floating_texts = [t for t in self.floating_texts if t.update()]

    def draw(self, screen):
        screen.fill(config.BG_COLOR)

        if self.state == config.MENU:
            self.draw_menu(screen)
        elif self.state == config.PLAYING:
            self.draw_game(screen)
            self.draw_sidebar(screen)
        elif self.state == config.GAME_OVER:
            self.draw_game(screen) # Draw game in background
            self.draw_overlay(screen, "GAME OVER", config.RED)
        elif self.state == config.VICTORY:
            self.draw_game(screen)
            self.draw_overlay(screen, "VICTORY!", config.GOLD)

    def draw_menu(self, screen):
        # Animated background
        for i in range(20):
            x = (pygame.time.get_ticks() // 50 + i * 50) % (config.WIDTH + 100) - 50
            y = 100 + i * 30
            pygame.draw.circle(screen, (44, 95, 61), (x, y), 20)

        title = self.title_font.render("TOWER DEFENSE", True, config.BLACK)
        screen.blit(title, (config.WIDTH // 2 - title.get_width()//2 + 3, config.HEIGHT // 4 + 3))
        title = self.title_font.render("TOWER DEFENSE", True, config.WHITE)
        screen.blit(title, (config.WIDTH // 2 - title.get_width()//2, config.HEIGHT // 4))

        start_btn = Button(config.WIDTH // 2 - 100, config.HEIGHT // 2, 200, 50, "START GAME", lambda: self.set_state(config.PLAYING))
        start_btn.draw(screen)

        load_btn = Button(config.WIDTH // 2 - 100, config.HEIGHT // 2 + 70, 200, 50, "LOAD GAME", self.load_from_file, color=config.BLUE)
        load_btn.draw(screen)

        # Handle buttons manually in main loop or add logic here.
        # For simplicity in this structure, interaction handled in main.py via event loop

    def set_state(self, state):
        self.state = state

    def load_from_file(self):
        data = load_game()
        if data:
            self.money = data['money']
            self.lives = data['lives']
            self.wave = data['wave']
            self.score = data['score']
            self.towers = []
            for t_data in data['towers']:
                t = Tower(t_data['x'], t_data['y'], t_data['type'])
                t.level = t_data['level']
                t.kills = t_data['kills']
                # Recalculate stats based on level
                for _ in range(t.level - 1):
                    t.upgrade()
                self.towers.append(t)
            self.state = config.PLAYING

    def draw_game(self, screen):
        # Draw Path
        for i in range(len(self.path) - 1):
            pygame.draw.line(screen, config.DARK_BROWN, self.path[i], self.path[i + 1], 48)
        for i in range(len(self.path) - 1):
            pygame.draw.line(screen, config.BROWN, self.path[i], self.path[i + 1], 40)

        # Draw Grid Overlay
        mouse_pos = pygame.mouse.get_pos()
        gx, gy = mouse_pos[0] // config.GRID_SIZE, mouse_pos[1] // config.GRID_SIZE

        for y in range(config.GRID_HEIGHT):
            for x in range(config.GRID_WIDTH):
                if self.grid[y][x]:
                    rect = pygame.Rect(x * config.GRID_SIZE, y * config.GRID_SIZE, config.GRID_SIZE, config.GRID_SIZE)
                    occupied = any(t.x // config.GRID_SIZE == x and t.y // config.GRID_SIZE == y for t in self.towers)

                    # FIX: Only draw placement preview if we have a tower type selected to build
                    if not occupied and self.selected_tower_type is not None and x == gx and y == gy and mouse_pos[0] < config.PLAY_WIDTH:
                        cost = config.TOWER_TYPES[self.selected_tower_type]['cost']
                        color = (0, 200, 0, 100) if self.money >= cost else (200, 0, 0, 100)
                        s = pygame.Surface((config.GRID_SIZE, config.GRID_SIZE), pygame.SRCALPHA)
                        s.fill(color)
                        screen.blit(s, rect)

                        # Range Preview
                        tr = config.TOWER_TYPES[self.selected_tower_type]['range']
                        cx, cy = x * config.GRID_SIZE + config.GRID_SIZE // 2, y * config.GRID_SIZE + config.GRID_SIZE // 2
                        pygame.draw.circle(screen, (100, 100, 100), (cx, cy), tr, 1)

                    pygame.draw.rect(screen, (0, 80, 0), rect, 1)

        # Entities
        for t in self.towers: t.draw(screen, selected=(t == self.selected_tower))
        for e in self.enemies: e.draw(screen)
        for p in self.projectiles: p.draw(screen)
        for p in self.particles: p.draw(screen)
        for f in self.floating_texts: f.draw(screen)

        # Indicators
        pygame.draw.polygon(screen, config.GREEN, [(0, 260), (20, 280), (0, 300)])
        pygame.draw.polygon(screen, config.RED, [(config.PLAY_WIDTH, 260), (config.PLAY_WIDTH - 20, 280), (config.PLAY_WIDTH, 300)])

    def draw_overlay(self, screen, title_text, color):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render(title_text, True, color)
        screen.blit(title, (config.WIDTH // 2 - title.get_width()//2, config.HEIGHT // 3))

        sub = self.font.render("Click to Restart", True, config.WHITE)
        screen.blit(sub, (config.WIDTH // 2 - sub.get_width()//2, config.HEIGHT // 2))