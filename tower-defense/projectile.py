import pygame
import math
import config
import floating_text
import particle
from utils import distance

class Projectile:
    def __init__(self, x, y, target, tower):
        self.x = x
        self.y = y
        self.target = target
        self.tower = tower
        self.speed = tower.projectile_speed
        self.damage = tower.damage
        self.splash_radius = tower.splash_radius
        self.slow_amount = tower.slow_amount
        self.color = tower.color
        self.last_known_pos = (target.x, target.y)

    def update(self, enemies, particles, floating_texts):
        if self.target and self.target.health > 0:
            self.last_known_pos = (self.target.x, self.target.y)
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = distance((self.x, self.y), (self.target.x, self.target.y))

            if dist < 15:
                self.hit(self.target, enemies, particles, floating_texts)
                return False

            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        else:
            # Target dead or gone, move to last known position then vanish
            dx = self.last_known_pos[0] - self.x
            dy = self.last_known_pos[1] - self.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist < 10:
                return False # Vanish

            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

        return True

    def hit(self, target, enemies, particles, floating_texts):
        killed = target.take_damage(self.damage)

        # Show Damage
        floating_texts.append(
            floating_text.FloatingText(target.x, target.y - 20, int(self.damage), config.WHITE, size=20))

        if killed:
            self.tower.kills += 1
            for _ in range(12):
                particles.append(particle.Particle(target.x, target.y, target.color))

        if self.slow_amount > 0:
            target.apply_slow(self.slow_amount)

        if self.splash_radius > 0:
            for _ in range(8):
                particles.append(particle.Particle(self.x, self.y, config.ORANGE, lifetime=20))
            for enemy in enemies:
                if enemy != target:
                    enemy_dist = distance((self.x, self.y), (enemy.x, enemy.y))
                    if enemy_dist < self.splash_radius:
                        killed = enemy.take_damage(self.damage * 0.5)
                        floating_texts.append(
                            floating_text.FloatingText(enemy.x, enemy.y - 20, int(self.damage * 0.5), config.WHITE, size=20))
                        if killed:
                            self.tower.kills += 1

    def draw(self, surface):
        pygame.draw.circle(surface, config.WHITE, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 4)