import pygame
from ui.ui_utils import get_font

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.base_width = w
        self.color_inactive = (100, 100, 100)
        self.color_active = (255, 215, 0) # Gold
        # Active by default as requested
        self.active = True 
        self.color = self.color_active
        
        self.text = text
        self.font = get_font(32)
        self.placeholder = "Name"
        self.txt_surface = self.font.render(self.text, True, self.color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # Return text ONLY on Enter and if not empty
                    if self.text.strip():
                        return self.text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Limit to 12 chars and printable
                    if len(self.text) < 12 and event.unicode.isprintable():
                        self.text += event.unicode
        
        return None

    def update(self):
        # Resize the box if the text is too long.
        if self.text:
            width = max(self.base_width, self.font.size(self.text)[0] + 20)
        else:
            width = max(self.base_width, self.font.size(self.placeholder)[0] + 20)
            
        # Center the new rect on the old center
        center = self.rect.center
        self.rect.width = width
        self.rect.center = center

    def draw(self, screen):
        # Determine what to draw
        if not self.text and not self.active:
            # Placeholder mode (inactive & empty) -> usually we want placeholder to show even if active if empty? 
            # User said: "Si le texte est vide, affiche 'Name' en gris clair. Ce texte disparaît dès qu'on tape une lettre."
            # So if text is empty, show placeholder.
            display_text = self.placeholder
            text_color = (150, 150, 150)
        elif not self.text and self.active:
             display_text = self.placeholder
             text_color = (150, 150, 150)
        else:
            display_text = self.text
            text_color = self.color

        self.txt_surface = self.font.render(display_text, True, text_color)
        
        # Blit the text.
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
