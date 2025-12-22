import pygame
import os
from ui.ui_utils import resource_path

class SoundManager:
    def __init__(self, music_volume=0.1, sfx_volume=1.0, music_muted=False, sfx_muted=False):
        self.sounds = {}
        self.enabled = True
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self.music_muted = music_muted
        self.sfx_muted = sfx_muted
        
        try:
            pygame.mixer.init()
            self._load_sounds()
            self._load_music()
        except Exception as e:
            print(f"Warning: Sound system could not initialize: {e}")
            self.enabled = False

    def _load_sounds(self):
        """Load sound effects."""
        sound_files = {
            'move': 'assets/sounds/move.wav',
            'merge': 'assets/sounds/merge.wav',
            'gameover': 'assets/sounds/gameover.wav'
        }

        for name, rel_path in sound_files.items():
            full_path = resource_path(rel_path)
            if os.path.exists(full_path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(full_path)
                except Exception as e:
                    print(f"Failed to load sound {name}: {e}")
            else:
                print(f"Warning: Sound file not found: {full_path}")

    def _load_music(self):
        """Load and start background music."""
        music_path = resource_path("assets/sounds/background.wav")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                # Apply volume considering mute state
                effective_volume = 0.0 if self.music_muted else self.music_volume
                pygame.mixer.music.set_volume(effective_volume)
                pygame.mixer.music.play(-1)  # Loop infinitely
            except Exception as e:
                print(f"Failed to load music: {e}")
        else:
            print(f"Warning: Music file not found: {music_path}")

    def play(self, name):
        """Play a sound effect by name."""
        if not self.enabled or self.sfx_muted:
            return
            
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.set_volume(self.sfx_volume)
                sound.play()
            except Exception:
                pass

    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled and not self.music_muted:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def toggle_music_mute(self):
        """Toggle music mute state."""
        self.music_muted = not self.music_muted
        if self.enabled:
            try:
                effective_volume = 0.0 if self.music_muted else self.music_volume
                pygame.mixer.music.set_volume(effective_volume)
            except Exception:
                pass
        return self.music_muted

    def toggle_sfx_mute(self):
        """Toggle SFX mute state."""
        self.sfx_muted = not self.sfx_muted
        return self.sfx_muted
