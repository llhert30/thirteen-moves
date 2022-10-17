import pygame


def alpha_rect(surface, rect=None, color=(0, 0, 0), alpha=1):
    if rect is None:
        x, y, w, h = 0, 0, surface.get_width(), surface.get_height()
    else:
        x, y, w, h = rect

    rect = pygame.Surface((w, h))
    rect.set_alpha(alpha * 255)
    rect.fill(color)
    surface.blit(rect, (x, y))


def get_text_rect(text, font_size=60, font="ariablack"):
    font = pygame.freetype.SysFont(font, font_size)
    return font.get_rect(text)


def centered_text(surface, text, x=0, y=0, color=(0, 0, 0), font_size=60, font="arialblack"):
    font = pygame.freetype.SysFont(font, font_size)
    text_rect = font.get_rect(text)
    text_rect.center = x, y
    font.render_to(surface, text_rect.topleft, text, color)


def set_cursor_to_hand():
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)


def set_cursor_to_default():
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


class Text:
    def __init__(self, text, x, y, color=(0, 0, 0), highlighted_color=(0, 0, 0), font_size=60, font="arialblack"):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.highlighted_color = highlighted_color
        self.font_size = font_size
        self.font = "ariablack"

        self.rect = get_text_rect(text, font_size, font)
        self.highlighted = False

    def display(self, surface):
        if self.highlighted:
            set_cursor_to_hand()
            centered_text(surface, self.text, self.x, self.y, self.highlighted_color, self.font_size, self.font)
        else:
            set_cursor_to_default()
            centered_text(surface, self.text, self.x, self.y, self.color, self.font_size, self.font)

    def update(self, events):
        hovered = self.is_hovered(events)
        if hovered:
            self.highlighted = True
        else:
            self.highlighted = False

    def is_hovered(self, events):
        mouse_x, mouse_y = events.mouse_pos
        w, h = self.rect.w, self.rect.h
        if self.x-w <= mouse_x < self.x+w and self.y-h <= mouse_y < self.y+h:
            return True
        else:
            return False
