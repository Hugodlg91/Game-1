import pygame
import os
from ui.ui_utils import resource_path

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        try:
            pygame.mixer.init()
            self._load_sounds()
        except Exception as e:
            print(f"Warning: Sound system could not differ initialize: {e}")
            self.enabled = False

    def _load_sounds(self):
        # Define sound files
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
                    # Adjust volumes if needed
                    if name == 'move':
                        self.sounds[name].set_volume(0.4)
                    elif name == 'merge':
                        self.sounds[name].set_volume(0.6)
                except Exception as e:
                    print(f"Failed to load sound {name}: {e}")
            else:
                print(f"Warning: Sound file not found: {full_path}")

    def play(self, name):
        """Play a sound by name if enabled and loaded."""
        if not self.enabled:
            return
            
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass
