import pygame
import math
from utils import distance
import config
import projectile

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        stats = config.TOWER_TYPES[tower_type]
        self.cost = stats['cost']
        self.base_damage = stats['damage'] # Store base for leveling calculation
        self.damage = stats['damage']
        self.range = stats['range']
        self.fire_rate = stats['fire_rate']
        self.color = stats['color']
        self.projectile_speed = stats['projectile_speed']
        self.splash_radius = stats.get('splash_radius', 0)
        self.slow_amount = stats.get('slow_amount', 0)
        self.last_shot = 0
        self.level = 1
        self.target = None
        self.angle = 0
        self.kills = 0
        self.targeting_mode = 'first' # first, strong, close, weak

    def upgrade(self):
        if self.level < 3:
            self.level += 1
            # Apply multipliers to base stats to prevent compound errors
            self.damage = int(self.base_damage * (1.5 ** (self.level - 1)))
            self.range = int(self.range * 1.15)
            self.fire_rate *= 1.2
            return True
        return False

    def get_upgrade_cost(self):
        return int(self.cost * self.level * 0.8)

    def get_sell_value(self):
        # Simplified sell value based on total investment
        total_invested = self.cost
        for i in range(1, self.level):
            total_invested += int(self.cost * i * 0.8)
        return int(total_invested * 0.6)

    def find_target(self, enemies):
        # Filter enemies in range
        in_range = [e for e in enemies if distance((self.x, self.y), (e.x, e.y)) < self.range]

        if not in_range:
            self.target = None
            return None

        if self.targeting_mode == 'first':
            # Furthest along path (highest path_index, then closest to next node)
            self.target = max(in_range, key=lambda e: (e.path_index, -distance((e.x, e.y), e.path[min(e.path_index + 1, len(e.path)-1)])))
        elif self.targeting_mode == 'strong':
            self.target = max(in_range, key=lambda e: e.max_health)
        elif self.targeting_mode == 'weak':
            self.target = min(in_range, key=lambda e: e.max_health)
        else: # close
            self.target = min(in_range, key=lambda e: distance((self.x, self.y), (e.x, e.y)))

        if self.target:
            self.angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
        return self.target

    def shoot(self, current_time, projectiles):
        if self.target and current_time - self.last_shot > 1000 / self.fire_rate:
            self.last_shot = current_time
            projectiles.append(projectile.Projectile(self.x, self.y, self.target, self))
            return True
        return False

    def draw(self, surface, selected=False):
        # Draw range circle when selected
        if selected:
            s = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], 50), (self.range, self.range), self.range)
            pygame.draw.circle(s, self.color, (self.range, self.range), self.range, 2)
            surface.blit(s, (self.x - self.range, self.y - self.range))

        # Base
        pygame.draw.circle(surface, config.DARK_GRAY, (self.x, self.y), 18)
        pygame.draw.circle(surface, self.color, (self.x, self.y), 15)

        # Turret
        turret_length = 20 + self.level * 3
        end_x = self.x + math.cos(self.angle) * turret_length
        end_y = self.y + math.sin(self.angle) * turret_length
        pygame.draw.line(surface, config.DARK_GRAY, (self.x, self.y), (end_x, end_y), 8)
        pygame.draw.line(surface, config.WHITE, (self.x, self.y), (end_x, end_y), 4)

        # Level Stars
        for i in range(self.level):
            star_x = self.x - 8 + i * 8
            star_y = self.y - 25
            pygame.draw.polygon(surface, config.YELLOW, [
                (star_x, star_y - 5), (star_x + 2, star_y - 2), (star_x + 5, star_y - 2),
                (star_x + 3, star_y + 1), (star_x + 4, star_y + 5), (star_x, star_y + 2),
                (star_x - 4, star_y + 5), (star_x - 3, star_y + 1), (star_x - 5, star_y - 2),
                (star_x - 2, star_y - 2)
            ])