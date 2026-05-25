# launcher/utils/path.py
import os

def get_base_dir():
    """Возвращает корень проекта (где лежит bot.py и .env)"""
    current = os.path.abspath(__file__)
    # launcher/utils/path.py → launcher/utils → launcher → root
    return os.path.dirname(os.path.dirname(os.path.dirname(current)))


def get_env_path():
    return os.path.join(get_base_dir(), ".env")


def get_messages_path():
    return os.path.join(get_base_dir(), "data", "bot_messages.json")