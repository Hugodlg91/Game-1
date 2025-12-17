"""Animation system for smooth tile transitions in 2048 game.

Provides interpolation and easing for tile movements, merges, and spawns.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import copy


def ease_out_cubic(t: float) -> float:
    """Ease-out cubic easing function for smooth deceleration.
    
    Args:
        t: Progress from 0.0 to 1.0
        
    Returns:
        Eased value from 0.0 to 1.0
    """
    return 1 - pow(1 - t, 3)


def ease_out_back(t: float) -> float:
    """Ease-out back easing for slight overshoot effect.
    
    Args:
        t: Progress from 0.0 to 1.0
        
    Returns:
        Eased value (may slightly exceed 1.0 before settling)
    """
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


class TileAnimation:
    """Represents a single tile's animation data."""
    
    def __init__(self, value: int, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                 is_merge: bool = False, is_spawn: bool = False):
        self.value = value
        self.from_row, self.from_col = from_pos
        self.to_row, self.to_col = to_pos
        self.is_merge = is_merge
        self.is_spawn = is_spawn


class TileAnimator:
    """Manages animations for tile movements, merges, and spawns."""
    
    def __init__(self, duration_ms: int = 250, spawn_delay_ms: int = 100):
        self.duration_ms = duration_ms
        self.spawn_delay_ms = spawn_delay_ms
        self.animations: List[TileAnimation] = []
        self.spawn_animations: List[TileAnimation] = []
        self.elapsed_ms = 0.0
        self.current_board: List[List[int]] = []
        
    def is_animating(self) -> bool:
        """Check if any animations are currently running."""
        return self.elapsed_ms < self.duration_ms + self.spawn_delay_ms + 150
    
    def start_move_animation(self, old_board: List[List[int]], new_board: List[List[int]], 
                            direction: str) -> None:
        """Calculate and start animations based on board changes.
        
        Args:
            old_board: Board state before the move
            new_board: Board state after the move
            direction: Direction of movement ('up', 'down', 'left', 'right')
        """
        self.animations = []
        self.spawn_animations = []
        self.elapsed_ms = 0.0
        self.current_board = copy.deepcopy(new_board)
        
        size = len(new_board)
        
        # Track all tiles
        old_tiles_used = [[False] * size for _ in range(size)]
        new_tiles_used = [[False] * size for _ in range(size)]
        
        # Process based on direction
        if direction in ['left', 'right']:
            # Process row by row
            for row in range(size):
                # Get non-zero tiles in order
                if direction == 'left':
                    old_positions = [(row, c) for c in range(size) if old_board[row][c] != 0]
                    new_positions = [(row, c) for c in range(size) if new_board[row][c] != 0]
                else:  # right
                    old_positions = [(row, c) for c in range(size - 1, -1, -1) if old_board[row][c] != 0]
                    new_positions = [(row, c) for c in range(size - 1, -1, -1) if new_board[row][c] != 0]
                
                # Map old tiles to new tiles
                old_idx = 0
                new_idx = 0
                
                while new_idx < len(new_positions):
                    new_r, new_c = new_positions[new_idx]
                    new_val = new_board[new_r][new_c]
                    new_tiles_used[new_r][new_c] = True
                    
                    if old_idx >= len(old_positions):
                        break
                    
                    old_r, old_c = old_positions[old_idx]
                    old_val = old_board[old_r][old_c]
                    
                    # Check for merge
                    if (old_idx + 1 < len(old_positions) and 
                        old_val * 2 == new_val):
                        old_r2, old_c2 = old_positions[old_idx + 1]
                        old_val2 = old_board[old_r2][old_c2]
                        
                        if old_val == old_val2:
                            # Merge animation
                            self.animations.append(TileAnimation(
                                old_val, (old_r, old_c), (new_r, new_c), is_merge=True
                            ))
                            self.animations.append(TileAnimation(
                                old_val2, (old_r2, old_c2), (new_r, new_c), is_merge=True
                            ))
                            old_tiles_used[old_r][old_c] = True
                            old_tiles_used[old_r2][old_c2] = True
                            old_idx += 2
                            new_idx += 1
                            continue
                    
                    # Simple move
                    self.animations.append(TileAnimation(
                        old_val, (old_r, old_c), (new_r, new_c)
                    ))
                    old_tiles_used[old_r][old_c] = True
                    old_idx += 1
                    new_idx += 1
        
        else:  # up or down
            # Process column by column
            for col in range(size):
                # Get non-zero tiles in order
                if direction == 'up':
                    old_positions = [(r, col) for r in range(size) if old_board[r][col] != 0]
                    new_positions = [(r, col) for r in range(size) if new_board[r][col] != 0]
                else:  # down
                    old_positions = [(r, col) for r in range(size - 1, -1, -1) if old_board[r][col] != 0]
                    new_positions = [(r, col) for r in range(size - 1, -1, -1) if new_board[r][col] != 0]
                
                # Map old tiles to new tiles
                old_idx = 0
                new_idx = 0
                
                while new_idx < len(new_positions):
                    new_r, new_c = new_positions[new_idx]
                    new_val = new_board[new_r][new_c]
                    new_tiles_used[new_r][new_c] = True
                    
                    if old_idx >= len(old_positions):
                        break
                    
                    old_r, old_c = old_positions[old_idx]
                    old_val = old_board[old_r][old_c]
                    
                    # Check for merge
                    if (old_idx + 1 < len(old_positions) and 
                        old_val * 2 == new_val):
                        old_r2, old_c2 = old_positions[old_idx + 1]
                        old_val2 = old_board[old_r2][old_c2]
                        
                        if old_val == old_val2:
                            # Merge animation
                            self.animations.append(TileAnimation(
                                old_val, (old_r, old_c), (new_r, new_c), is_merge=True
                            ))
                            self.animations.append(TileAnimation(
                                old_val2, (old_r2, old_c2), (new_r, new_c), is_merge=True
                            ))
                            old_tiles_used[old_r][old_c] = True
                            old_tiles_used[old_r2][old_c2] = True
                            old_idx += 2
                            new_idx += 1
                            continue
                    
                    # Simple move
                    self.animations.append(TileAnimation(
                        old_val, (old_r, old_c), (new_r, new_c)
                    ))
                    old_tiles_used[old_r][old_c] = True
                    old_idx += 1
                    new_idx += 1
        
        # Find spawned tiles (in new_board but not accounted for)
        for r in range(size):
            for c in range(size):
                if new_board[r][c] != 0 and not new_tiles_used[r][c]:
                    # This is a newly spawned tile
                    self.spawn_animations.append(TileAnimation(
                        new_board[r][c], (r, c), (r, c), is_spawn=True
                    ))
    
    def update(self, dt_ms: float) -> None:
        """Update animation progress.
        
        Args:
            dt_ms: Delta time in milliseconds
        """
        self.elapsed_ms += dt_ms
    
    def get_render_tiles(self, cell_size: int, margin: int) -> List[Dict]:
        """Get list of tiles to render with their interpolated properties.
        
        Args:
            cell_size: Size of each cell in pixels
            margin: Margin between cells in pixels
            
        Returns:
            List of tile render data dictionaries
        """
        tiles = []
        
        # Calculate progress (0.0 to 1.0)
        move_progress = min(1.0, self.elapsed_ms / self.duration_ms)
        eased_progress = ease_out_cubic(move_progress)
        
        # Render moving/merging tiles
        for anim in self.animations:
            # Interpolate position
            from_x = margin + anim.from_col * (cell_size + margin)
            from_y = margin + anim.from_row * (cell_size + margin)
            to_x = margin + anim.to_col * (cell_size + margin)
            to_y = margin + anim.to_row * (cell_size + margin)
            
            x = from_x + (to_x - from_x) * eased_progress
            y = from_y + (to_y - from_y) * eased_progress
            
            # Merge effect: slight scale pulse at the end
            scale = 1.0
            if anim.is_merge and move_progress > 0.7:
                pulse_progress = (move_progress - 0.7) / 0.3
                scale = 1.0 + 0.15 * pulse_progress * (1 - pulse_progress) * 4
            
            # Calculate distance for Z-sorting (are we moving?)
            dist = abs(from_x - to_x) + abs(from_y - to_y)

            tiles.append({
                'value': anim.value,
                'x': x,
                'y': y,
                'scale': scale,
                'alpha': 255,
                'is_merge': anim.is_merge,
                'is_spawn': False,
                'dist': dist
            })
        
        # Render spawning tiles (delayed start)
        spawn_start_time = self.duration_ms + self.spawn_delay_ms
        if self.elapsed_ms >= spawn_start_time:
            spawn_progress = min(1.0, (self.elapsed_ms - spawn_start_time) / 150.0)
            spawn_eased = ease_out_back(spawn_progress)
            
            for anim in self.spawn_animations:
                x = margin + anim.to_col * (cell_size + margin)
                y = margin + anim.to_row * (cell_size + margin)
                
                # Calculate distance for Z-sorting (spawning tiles don't move)
                dist = 0
                
                tiles.append({
                    'value': anim.value,
                    'x': x,
                    'y': y,
                    'scale': max(0.0, min(1.0, spawn_eased)),
                    'alpha': int(255 * spawn_progress),
                    'is_merge': False,
                    'is_spawn': True,
                    'dist': dist
                })
        
        # Assign Z-index for proper layering
        # 0: Stationary/Merge Targets (Bottom)
        # 1: Moving Tiles (Middle)
        # 2: Spawning Tiles (Top)
        
        for tile in tiles:
            # Determine priority
            if 'is_spawn' in tile and tile['is_spawn']:
                priority = 2
            elif tile['dist'] > 0.01:  # Moving
                priority = 1
            else:  # Static or Merge Target (stationary)
                priority = 0
            tile['z_index'] = priority

        # Sort by Z-index
        tiles.sort(key=lambda t: t['z_index'])
        
        return tiles
    
    def get_static_board(self) -> List[List[int]]:
        """Get the current board state (for non-animated rendering)."""
        return self.current_board
