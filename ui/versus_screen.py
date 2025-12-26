"""Versus Mode Screen - Human vs AI with Multiple Modes."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import get_theme_colors, get_font, calculate_layout, draw_board
from ui.animations import TileAnimator
from core.game_2048 import Game2048
from core.ai_player import expectimax_choose_move
from core.settings import load_settings, save_settings


class VersusScreen(Screen):
    # Game states
    SELECT_DIFFICULTY = "SELECT_DIFFICULTY"
    SELECT_MODE = "SELECT_MODE"
    SELECT_DURATION = "SELECT_DURATION"
    PLAYING = "PLAYING"
    GAME_OVER = "GAME_OVER"
    
    # Game Modes
    MODE_RACE = "RACE TO 2048"
    MODE_TIME_ATTACK = "TIME ATTACK"
    
    # Difficulty settings (name, delay in ms)
    DIFFICULTIES = {
        "Easy": 1500,
        "Medium": 1000,
        "Hard": 750,
        "Demon": 500
    }
    
    # Durations for Time Attack (in seconds)
    DURATIONS = {
        "1 Minute": 60,
        "3 Minutes": 180,
        "5 Minutes": 300
    }
    
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        
        # State management
        self.state = self.SELECT_DIFFICULTY
        self.difficulty = None
        self.ai_delay = 0
        self.game_mode = None
        self.time_limit = 0  # In seconds
        
        # Load settings
        settings = load_settings()
        self.high_score = settings.get("highscore", 0)
        self.theme_name = settings.get("theme", "Classic")
        self.theme = get_theme_colors(self.theme_name)
        
        # Load key bindings
        keys = settings.get("keys", {"up": "w", "down": "s", "left": "a", "right": "d"})
        self.key_up = pygame.key.key_code(keys.get("up", "w"))
        self.key_down = pygame.key.key_code(keys.get("down", "s"))
        self.key_left = pygame.key.key_code(keys.get("left", "a"))
        self.key_right = pygame.key.key_code(keys.get("right", "d"))
        
        # Sound manager
        self.sound_manager = manager.sound_manager if hasattr(manager, 'sound_manager') else None
        
        # Game instances
        self.player_game = None
        self.ai_game = None
        self.player_animator = TileAnimator()
        self.ai_animator = TileAnimator()
        
        # Threading for smooth UI
        self.ai_thinking = False
        self.ai_pending_move = None
        
        # Timing
        self.last_ai_move_time = 0
        self.game_start_time = 0
        self.elapsed_time = 0
        self.remaining_time = 0
        
        # Winner tracking
        self.winner = None  # "player", "ai", or "tie"
        self.win_reason = ""
        
        # Back button
        self.back_button = Button(
            pygame.Rect(0, 0, 240, 80),
            "BACK",
            lambda: self.on_back(),
            bg=(200, 50, 50), fg=(255, 255, 255)
        )
    
    def on_back(self):
        """Return to main menu or previous state."""
        if self.state == self.PLAYING or self.state == self.GAME_OVER:
            # If playing or game over, confirm exit? For now just go to menu logic
            pass
        
        # Logic to return to menu
        settings = load_settings()
        if self.player_game and self.player_game.score > self.high_score:
            settings["highscore"] = self.player_game.score
        settings["theme"] = self.theme_name
        save_settings(settings)
        
        from ui.menu import MainMenuScreen
        self.manager.set_screen(MainMenuScreen(self.manager))
    
    def set_difficulty(self, difficulty: str):
        self.difficulty = difficulty
        self.ai_delay = self.DIFFICULTIES[difficulty]
        self.state = self.SELECT_MODE
        
    def set_mode(self, mode: str):
        self.game_mode = mode
        if mode == self.MODE_TIME_ATTACK:
            self.state = self.SELECT_DURATION
        else:
            self.start_game()
            
    def set_duration(self, label: str):
        self.time_limit = self.DURATIONS[label]
        self.start_game()
    
    def start_game(self):
        """Initialize a new game."""
        self.state = self.PLAYING
        
        # Create new game instances
        self.player_game = Game2048()
        self.ai_game = Game2048()
        self.player_animator = TileAnimator()
        self.ai_animator = TileAnimator()
        
        self.ai_thinking = False
        self.ai_pending_move = None
        
        # Reset timing
        current_time = pygame.time.get_ticks()
        self.last_ai_move_time = current_time
        self.game_start_time = current_time
        self.winner = None
        self.win_reason = ""
    
    def check_win_conditions(self):
        """Check if game ended based on current mode."""
        if self.state != self.PLAYING:
            return

        # Common check: Game Over (Stuck)
        player_stuck = not self.player_game.has_moves_available()
        ai_stuck = not self.ai_game.has_moves_available()
        
        if self.game_mode == self.MODE_RACE:
            # 1. Reach 2048
            for row in self.player_game.board:
                if 2048 in row:
                    self.winner = "player"
                    self.win_reason = "Reached 2048!"
                    self.end_game()
                    return
            for row in self.ai_game.board:
                if 2048 in row:
                    self.winner = "ai"
                    self.win_reason = "Reached 2048!"
                    self.end_game()
                    return
            
            # 2. Opponent Stuck -> Instant Win
            if player_stuck:
                self.winner = "ai"
                self.win_reason = "Opponent Eliminated!"
                self.end_game()
            elif ai_stuck:
                self.winner = "player"
                self.win_reason = "Opponent Eliminated!"
                self.end_game()
                
        elif self.game_mode == self.MODE_TIME_ATTACK:
            # 1. Timeout (Handled in update loop, but checked here too)
            if self.remaining_time <= 0:
                self.resolve_time_attack()
                return
                
            # 2. KO Rule: If you get stuck before time runs out, you lose
            if player_stuck:
                self.winner = "ai"
                self.win_reason = "Knockout!"
                self.end_game()
            elif ai_stuck:
                self.winner = "player"
                self.win_reason = "Knockout!"
                self.end_game()
    
    def resolve_time_attack(self):
        """Determine winner by score at timeout."""
        p_score = self.player_game.score
        a_score = self.ai_game.score
        
        if p_score > a_score:
            self.winner = "player"
            self.win_reason = "Time's Up - Higher Score!"
        elif a_score > p_score:
            self.winner = "ai"
            self.win_reason = "Time's Up - Higher Score!"
        else:
            self.winner = "tie"
            self.win_reason = "Time's Up - Draw!"
        self.end_game()
        
    def end_game(self):
        self.state = self.GAME_OVER
        if self.sound_manager:
            self.sound_manager.play("gameover")

    def handle_event(self, event):
        """Handle user input."""
        self.back_button.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.on_back()
            
            # State-specific handling
            if self.state == self.SELECT_DIFFICULTY:
                if event.key == pygame.K_1: self.set_difficulty("Easy")
                elif event.key == pygame.K_2: self.set_difficulty("Medium")
                elif event.key == pygame.K_3: self.set_difficulty("Hard")
                elif event.key == pygame.K_4: self.set_difficulty("Demon")
                
            elif self.state == self.SELECT_MODE:
                if event.key == pygame.K_1: self.set_mode(self.MODE_RACE)
                elif event.key == pygame.K_2: self.set_mode(self.MODE_TIME_ATTACK)
                
            elif self.state == self.SELECT_DURATION:
                if event.key == pygame.K_1: self.set_duration("1 Minute")
                elif event.key == pygame.K_2: self.set_duration("3 Minutes")
                elif event.key == pygame.K_3: self.set_duration("5 Minutes")
                
            elif self.state == self.PLAYING:
                self.handle_playing_input(event)
                
            elif self.state == self.GAME_OVER:
                if event.key == pygame.K_SPACE:
                    # Restart flow
                    self.state = self.SELECT_DIFFICULTY
                    self.difficulty = None
                    self.game_mode = None
    
    def handle_playing_input(self, event):
        moved = False
        old_board = [row[:] for row in self.player_game.board]
        move_dir = None
        
        if event.key in (pygame.K_LEFT, self.key_left):
            moved = self.player_game.move('left'); move_dir = 'left'
        elif event.key in (pygame.K_RIGHT, self.key_right):
            moved = self.player_game.move('right'); move_dir = 'right'
        elif event.key in (pygame.K_UP, self.key_up):
            moved = self.player_game.move('up'); move_dir = 'up'
        elif event.key in (pygame.K_DOWN, self.key_down):
            moved = self.player_game.move('down'); move_dir = 'down'
        
        if moved:
            if self.sound_manager: self.sound_manager.play("move")
            self.player_animator.start_move_animation(old_board, self.player_game.board, move_dir)
            self.check_win_conditions()

    def update(self):
        """Update game logic."""
        if self.state == self.PLAYING:
            dt = 1000 / 60
            self.player_animator.update(dt)
            self.ai_animator.update(dt)
            
            current_time = pygame.time.get_ticks()
            
            # Time Attack Timer
            if self.game_mode == self.MODE_TIME_ATTACK:
                elapsed_game_time = (current_time - self.game_start_time) / 1000.0
                self.remaining_time = max(0, self.time_limit - elapsed_game_time)
                if self.remaining_time <= 0:
                    self.resolve_time_attack()
            
            # AI Logic (Threaded)
            if not self.ai_thinking and not self.ai_pending_move:
                 if current_time - self.last_ai_move_time >= self.ai_delay:
                    self.start_ai_thread()
            
            # Apply AI Move if ready
            if self.ai_pending_move:
                move = self.ai_pending_move
                self.ai_pending_move = None
                self.last_ai_move_time = current_time
                
                # If AI returned None (error/no move found) but game not over, fallback to random
                if move is None and self.ai_game.has_moves_available():
                    print("AI returned None, using fallback random move.")
                    import random
                    valid_moves = []
                    for d in ["up", "down", "left", "right"]:
                        # Test if move valid
                        test_g = Game2048()
                        test_g.board = [row[:] for row in self.ai_game.board]
                        if test_g.move(d):
                            valid_moves.append(d)
                    if valid_moves:
                        move = random.choice(valid_moves)

                if move:
                    old_board = [row[:] for row in self.ai_game.board]
                    moved = self.ai_game.move(move)
                    if moved:
                        self.ai_animator.start_move_animation(old_board, self.ai_game.board, move)
                        self.check_win_conditions()
    
    def start_ai_thread(self):
        """Run AI in background thread."""
        if not self.ai_game.has_moves_available():
            return

        self.ai_thinking = True
        
        # Determine depth based on difficulty
        # Easy: 1, Medium: 2, Hard: 3, Demon: 4
        # Default to 2
        depth = 2
        if self.difficulty == "Easy": depth = 1
        elif self.difficulty == "Medium": depth = 2
        elif self.difficulty == "Hard": depth = 3
        elif self.difficulty == "Demon": depth = 4
        
        def task():
            try:
                # Copy board to ensure thread safety (though we just read it)
                # Actually expectimax is pure function on game object, but game object is mutable.
                # Better to pass a copy or ensure we don't mutate during think.
                # Since game doesn't mutate during 'thinking', raw object is OK strictly speaking
                # IF expectimax doesn't mutate it. It doesn't (it copies).
                move = expectimax_choose_move(self.ai_game, depth=depth)
                self.ai_pending_move = move
            except Exception as e:
                print(f"AI Crash: {e}")
                self.ai_pending_move = None
            finally:
                self.ai_thinking = False
        
        import threading
        t = threading.Thread(target=task, daemon=True)
        t.start()
    
    def draw(self):
        """Draw screen based on state."""
        try:
            surf = self.surface
            w, h = surf.get_size()
            
            # Refresh theme
            self.theme = get_theme_colors(self.theme_name)
            surf.fill(self.theme["bg"])
            
            if self.state == self.SELECT_DIFFICULTY:
                self.draw_difficulty_selection(surf, w, h)
            elif self.state == self.SELECT_MODE:
                self.draw_mode_selection(surf, w, h)
            elif self.state == self.SELECT_DURATION:
                self.draw_duration_selection(surf, w, h)
            elif self.state == self.PLAYING:
                self.draw_playing(surf, w, h)
            elif self.state == self.GAME_OVER:
                self.draw_game_over(surf, w, h)
            
            # Back button
            self.back_button.rect.x = 40
            self.back_button.rect.y = h - 120
            self.back_button.draw(surf)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in VersusScreen.draw: {e}")

    # --- Draw Helpers ---
    
    def draw_menu_options(self, surf, w, h, title, options):
        """Generic helper for menu screens."""
        center_x = w // 2
        center_y = h // 2
        
        # Title
        title_size = int(min(w, h) * 0.05) if w > 600 else 24
        title_font = get_font(title_size)
        title_txt = title_font.render(title, False, self.theme.get("text_light", (255, 255, 255)))
        title_rect = title_txt.get_rect(center=(center_x, center_y - h * 0.25))
        surf.blit(title_txt, title_rect)
        
        # Options
        opt_size = int(min(w, h) * 0.035) if w > 600 else 18
        opt_font = get_font(opt_size)
        desc_font = get_font(int(opt_size * 0.6))
        
        start_y = center_y - (len(options) * opt_size * 2.5) / 2 + 40
        
        for i, opt in enumerate(options):
            # opt is tuple: (label, desc) or just (label,)
            label = opt[0]
            desc = opt[1] if len(opt) > 1 else ""
            
            y = start_y + i * opt_size * 2.5
            
            label_txt = opt_font.render(label, False, self.theme.get("text_light", (255, 255, 255)))
            
            if desc:
                desc_txt = desc_font.render(desc, False, self.theme.get("text_dark", (200, 200, 200)))
                # Layout logic: Side-by-side if wide enough
                if w > 600:
                    total_w = label_txt.get_width() + 40 + desc_txt.get_width()
                    start_x = center_x - total_w / 2
                    surf.blit(label_txt, (start_x, y))
                    surf.blit(desc_txt, (start_x + label_txt.get_width() + 40, y + (label_txt.get_height() - desc_txt.get_height())//2))
                else:
                    surf.blit(label_txt, label_txt.get_rect(center=(center_x, y)))
                    surf.blit(desc_txt, desc_txt.get_rect(center=(center_x, y + label_txt.get_height() + 5)))
            else:
                surf.blit(label_txt, label_txt.get_rect(center=(center_x, y)))

    def draw_difficulty_selection(self, surf, w, h):
        self.draw_menu_options(surf, w, h, "SELECT DIFFICULTY", [
            ("1 - EASY", "1 move / 1.5s"),
            ("2 - MEDIUM", "1 move / 1.0s"),
            ("3 - HARD", "1 move / 0.75s"),
            ("4 - DEMON", "1 move / 0.5s")
        ])

    def draw_mode_selection(self, surf, w, h):
        self.draw_menu_options(surf, w, h, "SELECT GAME MODE", [
            ("1 - RACE TO 2048", "First to 2048 or Last Survivor"),
            ("2 - TIME ATTACK", "Highest Score Wins")
        ])
        
    def draw_duration_selection(self, surf, w, h):
         self.draw_menu_options(surf, w, h, "SELECT DURATION", [
            ("1 - 1 MINUTE", ""),
            ("2 - 3 MINUTES", ""),
            ("3 - 5 MINUTES", "")
        ])

    def draw_playing(self, surf, w, h):
        # Calculate dynamic element sizes
        label_size = int(min(w, h) * 0.04) if w > 600 else 20
        score_size = int(min(w, h) * 0.035) if w > 600 else 16
        
        label_font = get_font(label_size)
        score_font = get_font(score_size)
        
        # Estimate height needed for text above board
        # Header (Timer/Title) + Gap + Label + Gap + Score + Gap
        header_text_height = int(label_size * 2)
        text_area_height = header_text_height + 10 + label_size + 5 + score_size + 15
        
        header_height = int(h * 0.1) if h > 600 else 60
        footer_height = 80
        
        available_h = h - header_height - footer_height - text_area_height
        gap = 50
        single_board_w = (w - (gap * 3)) // 2
        
        # Cap max size for 4K so they aren't massive
        if single_board_w > 800: single_board_w = 800
        
        if single_board_w < 100: single_board_w = w - 40
            
        layout = calculate_layout(single_board_w, available_h, 4)
        cell_size = layout["cell_size"]
        margin = layout["margin"]
        board_px = layout["board_size_px"]
        
        left_board_x = (w - (board_px * 2 + gap)) // 2
        right_board_x = left_board_x + board_px + gap
        
        total_content_height = text_area_height + board_px
        start_y_content = header_height + (h - header_height - footer_height - total_content_height) // 2
        if start_y_content < header_height + 10: start_y_content = header_height + 10
        
        # Y Positions
        timer_y = start_y_content + header_text_height // 2
        label_y = start_y_content + header_text_height + 10
        score_y = label_y + label_size + 5
        board_y = score_y + score_size + 15
        
        # --- Draw Info Header (Center) ---
        center_font = get_font(int(label_size * 0.8))
        if self.game_mode == self.MODE_RACE:
            mode_txt = center_font.render("RACE TO 2048", False, (255, 215, 0)) # Gold
            surf.blit(mode_txt, mode_txt.get_rect(center=(w//2, timer_y)))
        elif self.game_mode == self.MODE_TIME_ATTACK:
            # Timer formatting
            mins = int(self.remaining_time) // 60
            secs = int(self.remaining_time) % 60
            time_str = f"{mins:02}:{secs:02}"
            
            # Alert Color if low time
            color = (255, 255, 255)
            if self.remaining_time < 10:
                # Blink effect or just red
                if int(self.remaining_time * 4) % 2 == 0: # Fast flash
                    color = (255, 50, 50)
            
            timer_font = get_font(int(label_size * 1.5))
            timer_txt = timer_font.render(time_str, False, color)
            surf.blit(timer_txt, timer_txt.get_rect(center=(w//2, timer_y)))

        # Player Info
        you_txt = label_font.render("YOU", False, self.theme.get("text_light", (255, 255, 255)))
        surf.blit(you_txt, you_txt.get_rect(centerx=left_board_x + board_px // 2, top=label_y))
        
        p_score_txt = score_font.render(f"SCORE: {self.player_game.score}", False, (50, 255, 50))
        surf.blit(p_score_txt, p_score_txt.get_rect(centerx=left_board_x + board_px // 2, top=score_y))
        
        # AI Info
        ai_label = f"AI ({self.difficulty.upper()})"
        ai_txt = label_font.render(ai_label, False, self.theme.get("text_light", (255, 255, 255)))
        surf.blit(ai_txt, ai_txt.get_rect(centerx=right_board_x + board_px // 2, top=label_y))
        
        ai_score_txt = score_font.render(f"SCORE: {self.ai_game.score}", False, (255, 50, 50))
        surf.blit(ai_score_txt, ai_score_txt.get_rect(centerx=right_board_x + board_px // 2, top=score_y))
        
        # Draw Boards
        draw_board(surf, self.player_game, left_board_x, board_y, cell_size, margin, self.theme_name, self.player_animator)
        draw_board(surf, self.ai_game, right_board_x, board_y, cell_size, margin, self.theme_name, self.ai_animator)

    def draw_game_over(self, surf, w, h):
        self.draw_playing(surf, w, h)
        
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))
        
        center_x, center_y = w // 2, h // 2
        
        # Dynamic vertical spacing based on screen height
        spacing = h * 0.08  # Base unit for spacing
        
        # Winner
        win_font = get_font(int(min(w, h) * 0.08) if w > 600 else 40)
        col = (50, 255, 50) if self.winner == "player" else (255, 50, 50)
        if self.winner == "tie": col = (255, 255, 50); text = "DRAW!"
        elif self.winner == "player": text = "YOU WIN!"
        else: text = "AI WINS!"
        
        win_txt = win_font.render(text, False, col)
        win_rect = win_txt.get_rect(center=(center_x, center_y - spacing * 2))
        surf.blit(win_txt, win_rect)
        
        # Reason
        reason_font = get_font(int(min(w, h) * 0.04))
        rea_txt = reason_font.render(self.win_reason, False, (255, 255, 255))
        rea_rect = rea_txt.get_rect(center=(center_x, center_y - spacing * 0.8))
        surf.blit(rea_txt, rea_rect)
        
        # Final Scores
        sc_font = get_font(int(min(w, h) * 0.03))
        sc_txt = sc_font.render(f"YOU: {self.player_game.score}  -  AI: {self.ai_game.score}", False, (200, 200, 200))
        sc_rect = sc_txt.get_rect(center=(center_x, center_y + spacing * 0.5))
        surf.blit(sc_txt, sc_rect)
        
        # Instructions
        ins_font = get_font(int(min(w, h) * 0.025))
        ins_txt = ins_font.render("Press SPACE to Play Again | ESC to Quit", False, (150, 150, 150))
        ins_rect = ins_txt.get_rect(center=(center_x, center_y + spacing * 1.5))
        surf.blit(ins_txt, ins_rect)
