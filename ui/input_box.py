import pygame
from ui.ui_utils import get_font

class InputBox:
    def __init__(self, x, y, w, h, text='Player'):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (100, 100, 100)
        self.color_active = (255, 215, 0) # Gold
        self.color = self.color_inactive
        self.text = text
        self.active = False
        self.font = get_font(32)
        self.txt_surface = self.font.render(text, True, self.color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
            # Update the text surface even if we just clicked, in case color change triggers needed redraw
            self.txt_surface = self.font.render(self.text, True, self.color)
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text # Return authenticated text on Enter
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Limit to 12 chars and printable
                    if len(self.text) < 12 and event.unicode.isprintable():
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)
        return None

    def draw(self, screen):
        # Blit the text.
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
