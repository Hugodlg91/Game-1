import requests
import json

GAME_API_KEY = "dev_40da32792a654b99982ba75327e4a8b0"
LEADERBOARD_ID = "32471"
LEADERBOARD_KEY = "global_high_scores"

def get_token():
    auth_url = "https://api.lootlocker.io/game/v2/session/guest"
    resp = requests.post(auth_url, json={"game_key": GAME_API_KEY, "game_version": "1.0.0"}, headers={"Content-Type": "application/json"})
    if resp.status_code == 200:
        return resp.json().get('session_token')
    return None

def test_url(token, url, desc):
    print(f"--- Testing {desc} ---")
    print(f"URL: {url}")
    payload = {"score": "100", "member_id": "Guest", "metadata": "Debug"}
    headers = {"x-session-token": token, "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

def run():
    token = get_token()
    if not token:
        print("Auth Failed")
        return

    # 1. Standard v1 with ID
    test_url(token, f"https://api.lootlocker.io/game/v1/leaderboards/{LEADERBOARD_ID}/submit", "v1 with ID")
    
    # 2. Standard v1 with Key
    test_url(token, f"https://api.lootlocker.io/game/v1/leaderboards/{LEADERBOARD_KEY}/submit", "v1 with Key")
    
    # 3. No 'v1' with ID
    test_url(token, f"https://api.lootlocker.io/game/leaderboards/{LEADERBOARD_ID}/submit", "No v1 with ID")

    # 4. 'v2' ?? (Rare but possible)
    test_url(token, f"https://api.lootlocker.io/game/v2/leaderboards/{LEADERBOARD_ID}/submit", "v2 with ID")

if __name__ == "__main__":
    run()
