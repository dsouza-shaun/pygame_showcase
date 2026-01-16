import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, velocity=None, lifetime=30, size=4):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        if velocity:
            self.vx, self.vy = velocity
        else:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)