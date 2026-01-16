import pygame
import math
import config
from utils import distance

class Enemy:
    def __init__(self, path, enemy_type, wave_multiplier=1.0):
        self.path = path
        self.path_index = 0
        self.x = float(path[0][0])
        self.y = float(path[0][1])
        self.enemy_type = enemy_type
        stats = config.ENEMY_TYPES[enemy_type]
        self.max_health = int(stats['health'] * wave_multiplier)
        self.health = self.max_health
        self.base_speed = stats['speed']
        self.speed = self.base_speed
        self.reward = int(stats['reward'] * wave_multiplier)
        self.color = stats['color']
        self.size = stats['size']
        self.slow_timer = 0
        self.heals = stats.get('heals', False)
        self.heal_timer = 0
        self.frozen = False

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def apply_slow(self, amount):
        if not self.frozen:
            self.speed = self.base_speed * (1 - amount)
            self.slow_timer = pygame.time.get_ticks()

    def freeze(self):
        self.speed = 0
        self.frozen = True

    def update(self, enemies, particles, floating_texts):
        current_time = pygame.time.get_ticks()

        # Check slow expiry
        if self.slow_timer > 0 and current_time - self.slow_timer > 2000:
            self.speed = self.base_speed
            self.slow_timer = 0

        # Healer ability
        if self.heals and not self.frozen and current_time - self.heal_timer > 3000:
            self.heal_timer = current_time
            healed_count = 0
            for enemy in enemies:
                if enemy != self and enemy.health < enemy.max_health:
                    dist = distance((self.x, self.y), (enemy.x, enemy.y))
                    if dist < 80:
                        enemy.health = min(enemy.max_health, enemy.health + 20)
                        healed_count += 1

            if healed_count > 0:
                # Visual feedback for healing
                particles.append(
                    type('obj', (object,), {'x': self.x, 'y': self.y, 'color': (200, 255, 200), 'update': lambda: True, 'draw': lambda s: None})() # Simple dummy particle for trigger
                )
                # Ideally add specific heal particle effect here

        if self.path_index >= len(self.path) - 1:
            return 'reached_end'

        if self.health <= 0:
            return 'dead'

        # Move towards next waypoint
        target = self.path[self.path_index + 1]
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist < self.speed:
            self.path_index += 1
            if self.path_index < len(self.path):
                self.x = float(self.path[self.path_index][0])
                self.y = float(self.path[self.path_index][1])
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

        return 'alive'

    def draw(self, surface):
        # Draw shadow
        pygame.draw.ellipse(surface, (0, 0, 0, 100),
                            (self.x - self.size, self.y + self.size - 4, self.size * 2, 8))

        # Draw enemy body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, config.BLACK, (int(self.x), int(self.y)), self.size, 2)

        if self.enemy_type == 'boss':
            pygame.draw.circle(surface, config.WHITE, (int(self.x), int(self.y)), self.size - 8, 3)

        if self.slow_timer > 0 or self.frozen:
            pygame.draw.circle(surface, config.CYAN, (int(self.x), int(self.y)), self.size + 4, 2)

        # Health bar
        bar_width = self.size * 2 + 4
        bar_height = 6
        health_ratio = self.health / self.max_health
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size - 12

        pygame.draw.rect(surface, config.DARK_GRAY, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(surface, config.RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, config.GREEN, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))