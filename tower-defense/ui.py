import pygame
import config

class Button:
    def __init__(self, x, y, w, h, text, callback, color=config.GREEN, text_color=config.WHITE, hover_color=config.LIGHT_GREEN, tag=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.tag = tag
        self.is_active = False
        self.font = pygame.font.Font(None, 24)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        # Determine background color
        if self.is_active:
            # FIX: Clamp values to 255 so they don't go out of bounds
            r = min(255, self.color[0] + 30)
            g = min(255, self.color[1] + 30)
            b = min(255, self.color[2] + 30)
            color = (r, g, b)
        elif self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.color

        # Draw background
        pygame.draw.rect(surface, color, self.rect, border_radius=5)

        # Draw Border
        border_color = config.WHITE if self.is_active else (80, 80, 80)
        border_width = 3 if self.is_active else 1
        pygame.draw.rect(surface, border_color, self.rect, border_width, border_radius=5)

        # Draw Text
        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

# Helper for drawing icons/info
def draw_icon_text(surface, text, x, y, color=config.WHITE, font_size=22):
    font = pygame.font.Font(None, font_size)
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))