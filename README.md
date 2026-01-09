# Pygame Showcase

A collection of small, polished games built using **Python (3.13+)** and **Pygame**.  
This repository is meant for learning, experimentation, and showcasing Python-based game development.

Each game is self-contained in its own folder and includes everything needed to run or study it.

---

## Repository Structure

Each game folder contains:

- Python source code (`.py`)
- Pre-built Windows executable (`.exe`)
- `requirements.txt`
- A dedicated README explaining gameplay, controls, and features

This structure keeps each game isolated and easy to explore.

---

## Games Included

### 1. Snake Game

![Snake Game Preview](snake-game/preview.png)

A modern version of the classic Snake game featuring:

- Smooth movement and clean UI
- Screen wrapping (no wall collision)
- Increasing speed as score increases
- Golden food worth +3 points
- Special timed food mechanics
- No instant death on boundaries

**Folder:** `snake-game/`  
Includes `snake_game.exe` for Windows users in the `snake-game/dist/` folder

---

### 2. Chrome Dino

![Chrome Dino Preview](chrome-dino/preview.png)

A faithful recreation of the classic Chrome Dino Run game featuring:

- Smooth running, jumping, and ducking animations
- Accurate hitbox-based collision detection
- Progressive speed increase with score
- Classic zero-padded score display (e.g. 000089)
- Flying birds and ground obstacles
- Infinite scrolling ground
- Clean start and restart screen

**Folder:** `chrome-dino/`

More games will be added over time.

---

## Running Games from Source

### Recommended: Create a Virtual Environment

It is **strongly recommended** to run these games inside a virtual environment (venv).  
This keeps dependencies isolated and avoids conflicts with other Python projects.

### Create a Virtual Environment

From the project root:

```bash
python -m venv venv
```

### Activate the Virtual Environment

**Windows (PowerShell / CMD):**
```bash
venv\Scripts\activate
```
**macOS:**
```
source venv/bin/activate
```

### Install Dependencies

**With the virtual environment activated:**
```bash
pip install -r requirements.txt
```
**Or install Pygame directly:**
```bash
pip install pygame
```

---

## Run a game

### Navigate to the game folder and run:
```bash
python main.py
```

---

## License

This project is licensed under the MIT License.  
See the `LICENSE` file for details.