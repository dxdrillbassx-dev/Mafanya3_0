# launcher/main.py
import sys
import os

# Добавляем папку launcher в путь, чтобы импорты работали
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from launcher.ui import RetroLauncherUI

if __name__ == "__main__":
    launcher = RetroLauncherUI()
    launcher.run()