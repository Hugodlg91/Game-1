import pygame
import os

def create_pixel_icon():
    pygame.init()
    # Create a 24x24 surface with alpha channel
    surface = pygame.Surface((24, 24), pygame.SRCALPHA)
    
    # Colors
    c = (0, 0, 0, 255)  # Black solid
    t = (0, 0, 0, 0)    # Transparent
    
    # 24x24 grid pattern for a circular arrow
    # This is a hand-designed pixel art pattern
    pixels = [
        "                        ",
        "                        ",
        "         xxxxxx         ",
        "       xx      xx       ",
        "      x          x      ",
        "     x            x     ",
        "    x              x    ",
        "    x              xx   ",
        "   x                xx  ",
        "   x                 xx ",
        "   x                  x ",
        "   x                  x ",
        "   x                  x ",
        "   x                  x ",
        "   x                  x ",
        "    x                 x ",
        "    x                x  ",
        "     x              x   ",
        "      x            x    ",
        "       xx        xx     ",
        "         xxxxxx  x      ",
        "                xxx     ",
        "               xxxxx    ",
        "                        "
    ]
    
    # A improved circular arrow design
    pixels_better = [
        "                        ",
        "          xxxx          ",
        "       xxx    xxx       ",
        "     xx          xx     ",
        "    x              x    ",
        "   x                x   ",
        "   x                xx  ",
        "  x                  x  ",
        "  x                  xx ",
        "  x                   x ",
        "  x                   x ",
        "  x                   x ",
        "  x                   x ",
        "  x                   x ",
        "  x                  x  ",
        "   x                 x  ",
        "   x                 x  ",
        "    x               x   ",
        "     xx           xx    ",
        "       xxx      xx      ",
        "          xxxx  x       ",
        "               xxx      ",
        "              xxxxx     ",
        "             xxxxxxx    "
    ]
    
    # Even simpler, thicker one for readability
    pixels_thick = [
        "                        ",
        "         xxxxxx         ",
        "       xx      xx       ",
        "      x          x      ",
        "     x            x     ",
        "    x              x    ",
        "    x              xx   ",
        "   x                x   ",
        "   x                    ",
        "   x                    ",
        "   x                    ",
        "   x                    ",
        "   x                    ",
        "   x                    ",
        "   x                x   ",
        "    x               x   ",
        "    x              xx   ",
        "     x             x    ",
        "      x           xx    ",
        "       xx       xxx     ",
        "         xxxxxx   x     ",
        "                 xxx    ",
        "                xxxxx   ",
        "                        "
    ]

    # Let's use a procedurally drawn one on the surface to get it nicer but saved as pixels
    # Actually, drawing primitives on a small surface often looks distinctively "pixel art" if checking aliasing
    # But let's stick to the manual bitmask for absolute control
    
    # Let's try to map the thick pattern
    for y in range(24):
        row = pixels_thick[y]
        for x in range(len(row)):
            if x < 24 and row[x] == 'x':
                surface.set_at((x, y), c)
    
    # Save the file
    out_path = os.path.join("ui", "reset_icon.png")
    pygame.image.save(surface, out_path)
    print(f"Created {out_path}")

if __name__ == "__main__":
    create_pixel_icon()
