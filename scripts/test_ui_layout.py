import sys
import os
import pygame

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.ui_utils import calculate_layout

def test_layout(width, height):
    print(f"Testing Layout for {width}x{height}...")
    
    layout = calculate_layout(width, height)
    
    # Extract Board Rect
    board_size = layout['board_size_px']
    start_x = layout['start_x']
    start_y = layout['center_y'] # Note: ui_utils calls it center_y but it's the top-left Y of board potentially? 
    # Checking ui_utils.py: start_y = (screen_h - real_board_px) // 2. Yes it is top-left of board centered vertically.
    
    board_rect = pygame.Rect(start_x, start_y, board_size, board_size)
    
    # Simulate Header Rect
    # In PlayScreen typically:
    # Title is at top with margin. Score is below title? Or side by side?
    # Let's assume a generic header area of top 15% or fixed pixels.
    # Looking at typical 2048 layout: Header is above board.
    
    # Check if board overlaps with likely header area
    # If board is vertically centered, does it leave enough space at top?
    
    top_space = start_y
    required_top_space = int(height * 0.15) # Assume we need 15% for header
    if required_top_space < 100: required_top_space = 100 # Min header height
    
    print(f"  Board Rect: {board_rect}")
    print(f"  Top Space Available: {top_space}px")
    print(f"  Required Top Space (Est): {required_top_space}px")
    
    if top_space < required_top_space:
        print("  [FAIL] potential overlap! Board is too high.")
    else:
        print("  [PASS] Layout looks safe.")
        
    # Check bounds
    if board_rect.bottom > height:
         print("  [FAIL] Board goes off-screen bottom!")
    if board_rect.right > width:
         print("  [FAIL] Board goes off-screen right!")
         
    print("-" * 20)

if __name__ == "__main__":
    resolutions = [
        (1280, 720),
        (1366, 768),
        (1920, 1080),
        (2560, 1440)
    ]
    
    for w, h in resolutions:
        test_layout(w, h)
