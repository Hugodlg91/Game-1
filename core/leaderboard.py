try:
    import requests
except ImportError:
    requests = None
    print("Warning: 'requests' library not found. Online Leaderboard disabled.")

import json
import threading

class LeaderboardManager:
    # --- CONFIGURATION LOOTLOCKER ---
    # Remplace par ta clé API publique (Settings -> API Keys)
    GAME_API_KEY = "dev_40da32792a654b99982ba75327e4a8b0"
    # Remplace par la clé de ton leaderboard (Systems -> Leaderboards)
    LEADERBOARD_KEY = "32471" 
    
    API_URL = "https://api.lootlocker.io/game/v2/session/guest"
    # Note: '/v1/' removed as it was returning 404. Using root path which was found.
    LEADERBOARD_URL = f"https://api.lootlocker.io/game/leaderboards/{LEADERBOARD_KEY}"

    _session_token = None
    _player_id = None

    @classmethod
    def start_session(cls):
        """Authentifie le joueur en tant qu'invité (Guest)"""
        if requests is None:
            return False

        if cls._session_token:
            return True # Déjà connecté

        headers = {"Content-Type": "application/json"}
        payload = {"game_key": cls.GAME_API_KEY, "game_version": "1.0.0"}

        try:
            response = requests.post(cls.API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                cls._session_token = data.get('session_token')
                cls._player_id = data.get('player_id')
                print(f"[ONLINE] Connecté. Player ID: {cls._player_id}")
                return True
            else:
                print(f"[ONLINE] Erreur Auth: {response.text}")
                return False
        except Exception as e:
            print(f"[ONLINE] Erreur Connexion: {e}")
            return False

    @classmethod
    def submit_score(cls, player_name, score):
        """Envoie le score. Bloquant, à utiliser idéalement dans un Thread."""
        if not cls._session_token:
            if not cls.start_session():
                return False

        url = f"{cls.LEADERBOARD_URL}/submit"
        headers = {
            "Content-Type": "application/json",
            "x-session-token": cls._session_token
        }
        # On envoie le score et le nom (metadata)
        payload = {"score": str(score), "member_id": str(cls._player_id), "metadata": player_name}

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"[ONLINE] Score envoyé pour {player_name}: {score}")
                # LootLocker ne permet pas toujours de set le nom directement via l'API Guest simple
                # sans configurer le player. Ici on utilise 'metadata' pour stocker le nom,
                # ou on configure le nom du joueur séparément.
                # Pour simplifier, on va aussi essayer de set le nom du joueur:
                cls.set_player_name(player_name)
                return True
            else:
                print(f"[ONLINE] Erreur Submit: {response.text}")
                return False
        except Exception as e:
            print(f"[ONLINE] Erreur: {e}")
            return False

    @classmethod
    def set_player_name(cls, name):
        """Définit le nom public du joueur"""
        url = "https://api.lootlocker.io/game/v1/player/name"
        headers = {"Content-Type": "application/json", "x-session-token": cls._session_token}
        payload = {"name": name}
        try:
            requests.patch(url, json=payload, headers=headers)
        except:
            pass

    @classmethod
    def get_top_scores(cls, count=10):
        """Récupère le Top 10"""
        if not cls._session_token:
            cls.start_session()

        url = f"{cls.LEADERBOARD_URL}/list?count={count}"
        headers = {"x-session-token": cls._session_token}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                results = []
                for item in items:
                    rank = item.get('rank')
                    score = item.get('score')
                    # On essaie de récupérer le nom, sinon 'player' + id
                    player = item.get('player', {})
                    name = player.get('name') 
                    if not name: 
                        name = item.get('metadata') # Fallback si on a stocké dans metadata
                    if not name:
                        name = f"Player {item.get('member_id')}"
                    
                    results.append((rank, name, score))
                return results
            return []
        except Exception as e:
            print(f"[ONLINE] Erreur Get: {e}")
            return []
