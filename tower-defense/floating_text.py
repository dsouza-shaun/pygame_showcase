import pygame


class FloatingText:
    def __init__(self, x, y, text, color, size=24, speed=1):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.font = pygame.font.Font(None, size)
        self.lifetime = 60
        self.speed = speed

    def update(self):
        self.y -= self.speed
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        alpha = min(255, self.lifetime * 5)
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (self.x, self.y))