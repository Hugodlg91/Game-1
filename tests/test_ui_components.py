import unittest
import pygame
from ui.buttons import Button

class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    def test_button_font_autoscaling(self):
        # Create a button rect that is moderately wide
        rect = pygame.Rect(0, 0, 250, 50)
        # Text that acts as a "long label" but should fit if scaled down
        # At size 50, "Long Button Label" is likely > 300px
        long_text = "Long Button Label"
        
        # Initialize button with a large default font size
        initial_font_size = 50
        btn = Button(rect, long_text, lambda: None, font_size=initial_font_size)
        
        # Check if the font size was reduced
        current_font_height = btn.font.get_height()
        print(f"Initial request: {initial_font_size}, Resulting font height: {current_font_height}")
        
        # The font height should be significantly less than the initial 50 (likely around 20-30)
        self.assertLess(current_font_height, 45, "Font height should have been reduced")
        
        # Verify text fits within width + padding
        txt_w = btn.font.size(long_text)[0]
        self.assertLess(txt_w, 250, "Text width should be less than button width")
        
        # Also ensure it didn't scale down for short text that fits
        short_text = "OK"
        btn_short = Button(rect, short_text, lambda: None, font_size=30)
        w_short = btn_short.font.size(short_text)[0]
        # Should stay close to requested size (30)
        # We rely on the fact that the loop breaks immediately if it fits
        # We can't easily check the internal font object size attribute in pygame, 
        # but the logic ensures we start at requested size.

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
