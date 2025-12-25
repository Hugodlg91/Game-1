import requests
import json
import os
import uuid

class LeaderboardManager:
    # --- CONFIGURATION LOOTLOCKER ---
    GAME_API_KEY = "dev_40da32792a654b99982ba75327e4a8b0"
    LEADERBOARD_KEY = "32471" 
    
    API_URL = "https://api.lootlocker.io/game/v2/session/guest"
    LEADERBOARD_URL = f"https://api.lootlocker.io/game/leaderboards/{LEADERBOARD_KEY}"
    
    # Fichier de sauvegarde des identités
    ID_FILE = "player_ids.json"

    _session_token = None
    _current_player_id = None
    _current_player_name = None

    @classmethod
    def get_uuid_for_name(cls, name):
        """
        Cherche l'UUID associé à un nom spécifique.
        Si le nom est nouveau, on génère un nouvel UUID.
        """
        data = {}
        # 1. Charger le fichier existant
        if os.path.exists(cls.ID_FILE):
            try:
                with open(cls.ID_FILE, 'r') as f:
                    data = json.load(f)
            except:
                data = {}
        
        # 2. Vérifier si le nom existe déjà
        if name in data:
            return data[name]
        
        # 3. Sinon, créer un nouvel UUID pour ce nom
        new_uuid = str(uuid.uuid4())
        data[name] = new_uuid
        
        # 4. Sauvegarder
        try:
            with open(cls.ID_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[ONLINE] Erreur sauvegarde ID: {e}")
            
        return new_uuid

    @classmethod
    def start_session(cls, player_name="Spectator"):
        """
        Démarre une session. 
        Si on fournit un player_name, on se connecte avec l'identité de ce nom.
        Sinon (pour juste regarder le leaderboard), on utilise une identité 'Spectator'.
        """
        # Si on est déjà connecté avec le bon nom, on ne fait rien
        if cls._session_token and cls._current_player_name == player_name:
            return True

        # Récupère l'UUID unique lié à CE nom précis
        player_identifier = cls.get_uuid_for_name(player_name)

        headers = {"Content-Type": "application/json"}
        payload = {
            "game_key": cls.GAME_API_KEY, 
            "game_version": "1.0.0",
            "player_identifier": player_identifier
        }

        try:
            response = requests.post(cls.API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                cls._session_token = data.get('session_token')
                cls._current_player_id = data.get('player_id')
                cls._current_player_name = player_name # On retient qui est connecté
                print(f"[ONLINE] Connecté en tant que '{player_name}' (ID: {cls._current_player_id})")
                
                # Mise à jour forcée du nom sur LootLocker (pour être sûr que l'affichage est bon)
                if player_name != "Spectator":
                    cls.set_player_name_online(player_name)
                    
                return True
            else:
                print(f"[ONLINE] Erreur Auth: {response.text}")
                return False
        except Exception as e:
            print(f"[ONLINE] Erreur Connexion: {e}")
            return False

    @classmethod
    def set_player_name_online(cls, name):
        """Force le nom du joueur sur le serveur LootLocker"""
        url = "https://api.lootlocker.io/game/v1/player/name"
        headers = {"Content-Type": "application/json", "x-session-token": cls._session_token}
        payload = {"name": name}
        try:
            requests.patch(url, json=payload, headers=headers)
        except:
            pass

    @classmethod
    def submit_score(cls, player_name, score):
        """
        Connecte le joueur spécifique et envoie son score.
        """
        # Étape cruciale : On se RE-CONNECTE avec l'identité du nom saisi
        if not cls.start_session(player_name):
            return False

        url = f"{cls.LEADERBOARD_URL}/submit"
        headers = {
            "Content-Type": "application/json",
            "x-session-token": cls._session_token
        }
        
        payload = {
            "score": str(score), 
            "member_id": str(cls._current_player_id), 
            "metadata": player_name 
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"[ONLINE] Score envoyé pour {player_name}: {score}")
                return True
            else:
                print(f"[ONLINE] Erreur Submit: {response.text}")
                return False
        except Exception as e:
            print(f"[ONLINE] Erreur: {e}")
            return False

    @classmethod
    def get_top_scores(cls, count=10):
        """Récupère le Top 10"""
        # Pour lire les scores, on n'a pas besoin d'une identité précise, 
        # on utilise l'identité actuelle ou 'Spectator' par défaut.
        if not cls._session_token:
            cls.start_session("Spectator")

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
                    
                    # Priorité : Metadata > Player Name > ID
                    name = item.get('metadata')
                    if not name:
                        player = item.get('player', {})
                        name = player.get('name')
                    if not name:
                        name = f"Joueur {item.get('member_id')}"
                    
                    results.append((rank, name, score))
                return results
            return []
        except Exception as e:
            print(f"[ONLINE] Erreur Get: {e}")
            return []
