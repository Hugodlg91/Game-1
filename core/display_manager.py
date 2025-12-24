
import pygame

class DisplayManager:
    def __init__(self, initial_window_size, virtual_width=3840, virtual_height=2160):
        # ON TRAVAILLE EN 4K NATIVE
        # Tout ton code UI doit penser qu'il est sur un écran géant de 3840x2160.
        self.VIRTUAL_W = virtual_width
        self.VIRTUAL_H = virtual_height
        
        # Surface de rendu haute définition
        self.virtual_surface = pygame.Surface((self.VIRTUAL_W, self.VIRTUAL_H))
        
        # L'écran réel (fenêtre redimensionnable)
        self.real_screen = pygame.display.set_mode(initial_window_size, pygame.RESIZABLE)
        
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        self.resize(initial_window_size[0], initial_window_size[1])

    def resize(self, new_w, new_h):
        """Recalcule le ratio pour faire rentrer la 4K dans la fenêtre"""
        # On calcule le ratio (ex: sur un écran 1080p, scale sera de 0.5)
        scale_w = new_w / self.VIRTUAL_W
        scale_h = new_h / self.VIRTUAL_H
        self.scale = min(scale_w, scale_h)
        
        final_w = int(self.VIRTUAL_W * self.scale)
        final_h = int(self.VIRTUAL_H * self.scale)
        
        # Centrage (Letterboxing)
        self.offset_x = (new_w - final_w) // 2
        self.offset_y = (new_h - final_h) // 2

    def convert_event(self, event):
        """Traduit les clics de la petite fenêtre vers la surface 4K"""
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            real_x, real_y = event.pos
            
            # Formule inverse : (Reel - Offset) / Scale = Virtuel
            # Si scale est 0.5 (écran 1080p), on multiplie par 2 pour retrouver la coord 4K
            if self.scale > 0:
                virt_x = int((real_x - self.offset_x) / self.scale)
                virt_y = int((real_y - self.offset_y) / self.scale)
                
                event.pos = (virt_x, virt_y)
                
                if event.type == pygame.MOUSEMOTION:
                    event.rel = (int(event.rel[0] / self.scale), int(event.rel[1] / self.scale))
                
        return event

    def draw(self):
        """Affiche le rendu final"""
        final_w = int(self.VIRTUAL_W * self.scale)
        final_h = int(self.VIRTUAL_H * self.scale)
        
        # Smoothscale est ESSENTIEL ici pour que le rétrécissement (4K -> 1080p) soit beau et pas pixelisé
        scaled_surface = pygame.transform.smoothscale(self.virtual_surface, (final_w, final_h))
        
        # Nettoyage (Bandes noires)
        self.real_screen.fill((10, 10, 10)) # Gris très sombre, plus élégant que noir pur
        
        # Affichage centré
        self.real_screen.blit(scaled_surface, (self.offset_x, self.offset_y))
        
        pygame.display.flip()
