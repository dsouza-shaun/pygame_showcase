import json
import math
import os

SAVE_FILE = "save_data.json"

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def save_game(game_state):
    """Save relevant game state to JSON."""
    data = {
        'money': game_state.money,
        'lives': game_state.lives,
        'wave': game_state.wave,
        'score': game_state.score,
        'towers': [],
        'enemies': [] # Simplified saving: we won't save active enemies to prevent bugs on load
    }

    for t in game_state.towers:
        data['towers'].append({
            'type': t.tower_type,
            'x': t.x,
            'y': t.y,
            'level': t.level,
            'kills': t.kills
        })

    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False

def load_game():
    """Load game state from JSON."""
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading game: {e}")
        return None