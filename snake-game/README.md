# Snake Game

![Snake Game Preview](snake-game/preview.png)

A fast, clean, and modern Snake game built using **Python 3.13** and **Pygame**.  
The game includes special golden food (+3 points), increasing speed, and smooth gameplay.

---

## Features
- Smooth snake movement  
- Golden special food (+3 points)  
- Increasing speed based on score  
- Screen wrapping  
- No wall deaths  
- Clean UI  
- EXE included for Windows users  

---

## Download & Play (Windows EXE)
Download the ready-to-play EXE:  
**snake_game.exe** (inside the dist folder)

Just double-click and play — *no installation needed*.

### The .exe files were made using pyinstaller

Used PyInstaller to generate a standalone executable without a console window.
You can do that as well.

### Command
Install pyinstaller first using pip
```
pip install pyinstaller
```

Run command
```
pyinstaller --onefile --noconsole --icon=icon.ico main.py
```

### Notes
- Replace main.py with your actual game file name
- icon.ico is optional (remove the flag if you don’t have one)
- The EXE will be generated inside the dist/ folder

---

## Run from Source (Python)
### Requirements
Python **3.13+**  
Install dependencies:
Package                   Version
------------------------- --------
pygame                    2.6.1

---

## License
This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute the code.
