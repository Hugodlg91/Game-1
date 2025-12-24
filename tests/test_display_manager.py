import unittest
import pygame
from core.display_manager import DisplayManager

class TestDisplayManager(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Mock display.set_mode to avoid opening actual window during test
        pygame.display.set_mode = lambda size, flags=0: pygame.Surface(size)
        # Default is now 4K
        self.dm = DisplayManager((1280, 720), virtual_width=3840, virtual_height=2160)

    def tearDown(self):
        pygame.quit()

    def test_initial_scaling(self):
        # 1280x720 is 16:9.
        # Scale should be 1280/3840 = 0.333...
        expected_scale = 1280 / 3840
        self.assertAlmostEqual(self.dm.scale, expected_scale)
        self.assertEqual(self.dm.offset_x, 0)
        self.assertEqual(self.dm.offset_y, 0)

    def test_letterbox_wide(self):
        # Resize to super wide window: 2000x500
        # Should be limited by height.
        # Scale = 500 / 2160 = 0.2314...
        self.dm.resize(2000, 500)
        expected_scale = 500 / 2160
        self.assertAlmostEqual(self.dm.scale, expected_scale)
        
        # Width used = 3840 * scale
        final_w = int(3840 * expected_scale)
        expected_offset_x = (2000 - final_w) // 2
        self.assertEqual(self.dm.offset_x, expected_offset_x)

    def test_letterbox_tall(self):
        # Resize to tall window: 1000x2000
        # Should be limited by width.
        # Scale = 1000 / 3840 = 0.2604...
        self.dm.resize(1000, 2000)
        expected_scale = 1000 / 3840
        self.assertAlmostEqual(self.dm.scale, expected_scale)
        
        # Height used = 2160 * scale
        final_h = int(2160 * expected_scale)
        expected_offset_y = (2000 - final_h) // 2
        self.assertEqual(self.dm.offset_y, expected_offset_y)

    def test_event_conversion(self):
        # Window 1280x720 (Scale 0.333...)
        scale = 1280/3840
        self.dm.resize(1280, 720)
        
        # Click at center of real screen (640, 360)
        # Should correspond to center of virtual screen (1920, 1080)
        mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (640, 360), 'button': 1})
        converted = self.dm.convert_event(mock_event)
        
        # Check tolerance (int conversion might be off by 1 pixel)
        self.assertAlmostEqual(converted.pos[0], 1920, delta=1)
        self.assertAlmostEqual(converted.pos[1], 1080, delta=1)

if __name__ == '__main__':
    unittest.main()
