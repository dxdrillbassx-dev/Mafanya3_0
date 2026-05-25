# utils/module_descriptions.py

MODULE_DESCRIPTIONS = {
    "basic": "Основные команды: ping, hello, about, clear и т.д.",
    "customrole": "Создание и управление личными ролями",
    "forza": "Интеграция с Forza Horizon 6",
    "fun": "Развлекательные команды",
    "gemini": "ИИ на базе Gemini",
    "helpimage": "Красивое меню команд",
    "maintenance": "Техническое обслуживание бота",
    "moderation": "Модерация сервера",
    "pinterest": "Поиск пинов на Pinterest",
    "reload": "Перезагрузка модулей",
    "structure": "Структура проекта",
    "vkphoto": "Рандомные фото из ВК",
    "voice_ai": "Голосовой ИИ (TTS)",
    "voice_stt": "Распознавание речи",
    "audio": "Музыкальный плеер",
    "audio_files": "Воспроизведение аудиофайлов из чата",
}

# Простая заглушка, чтобы не было RuntimeWarning
def get_message(section: str, key: str, default: str = "", **kwargs):
    """Если нужно — используй из bot.py"""
    return default