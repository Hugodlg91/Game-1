import pygame
import os

def create_game_icon():
    # Initialize pygame
    pygame.init()
    
    # Settings
    size = 256
    bg_color = (237, 194, 46)  # Typical 2048 gold/yellow color
    text_color = (249, 246, 242) # Off-white text
    
    # Create surface with alpha channel for transparency support (though saving as png)
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw rounded rectangle background
    rect = pygame.Rect(0, 0, size, size)
    # Draw main body
    pygame.draw.rect(surface, bg_color, rect, border_radius=40)
    
    # Draw border (optional, subtle)
    border_color = (187, 173, 160)
    pygame.draw.rect(surface, border_color, rect, width=4, border_radius=40)
    
    # Render Text "2048"
    try:
        # Try to use a system font that looks nice and bold
        font = pygame.font.SysFont("arial", int(size * 0.35), bold=True)
    except:
        font = pygame.font.Font(None, int(size * 0.4))

    text = font.render("2048", True, text_color)
    text_rect = text.get_rect(center=(size // 2, size // 2))
    
    # Blit text onto background
    surface.blit(text, text_rect)
    
    # Save as PNG
    output_png = "game_icon.png"
    pygame.image.save(surface, output_png)
    print(f"✅ Icon created successfully: {output_png}")
    
    # Quit pygame
    pygame.quit()

if __name__ == "__main__":
    create_game_icon()
