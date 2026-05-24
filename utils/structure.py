# utils/structure.py
"""
Утилита для показа структуры проекта
"""

import os


def get_project_structure() -> str:
    """Возвращает красивую структуру проекта"""
    return """
Mafanya 3.0 — Структура проекта
══════════════════════════════════════════════
bot.py
├── .env
├── cogs/
│   ├── init.py
│   ├── basic.py
│   ├── gemini.py
│   ├── helpimage.py
│   ├── customrole.py
│   ├── maintenance.py
│   ├── moderation.py
│   ├── forza.py
│   ├── fun.py
│   ├── pinterest.py
│   ├── reload.py
│   ├── structure.py
│   ├── vkphoto.py
│   ├── voice_ai.py
│   ├── voice_stt.py
│   └── audio/
│       ├── init.py
│       ├── audio.py
│       └── audio_files.py
├── utils/
│   ├── init.py
│   ├── aliases.py
│   ├── module_descriptions.py
│   ├── music_cover.py
│   └── structure.py
├── data/
│   ├── custom_roles.json
│   ├── forza_cars.json
│   └── pinterest_history.json
├── launcher/
│   ├── __init__.py
│   ├── main.py
│   ├── ui.py
│   ├── core.py
│   └── config.py
└── backgrounds/
└── (*.jpg, *.png файлы)
└── Mafanya.bat
"""
