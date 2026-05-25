# utils/aliases.py
import importlib
import os

# ====================== ОСНОВНЫЕ ДАННЫЕ ======================

COMMAND_ALIASES = {
    "about": ['бот', 'инфо'],
    "ban": ['бан'],
    "botstat": ['стат', 'стата', 'статистика', 'status'],
    "clear": ['очистить', 'purge'],
    "createrole": ['личная', 'мояроль', 'своя'],
    "eightball": ['8ball', 'шар', 'магическийшар'],
    "forza_status": ['forza', 'форза', 'форца'],
    "forzaprofile": ['forzadash', 'fd', 'dash', 'fprofile', 'forzainfo', 'finfo', 'форзапрофиль', 'профильфорза'],
    "hello": ['привет'],
    "helpimage": ['helpimg', 'меню', 'команды', 'himg', 'help'],
    "join_voice": ['join', 'зайди', 'voice'],
    "kick": ['кик'],
    "leave": ['dc', 'выйти', 'aleave'],
    "leave_voice": ['выйди', 'dis', 'leaveai'],
    "listcustomroles": ['личные', 'все_личные', 'adminroles'],
    "load": ['загрузить'],
    "meme": ['мем'],
    "mute": ['мут', 'timeout'],
    "myid": ['мойid', 'мойид'],
    "pause": ['пауза'],
    "ping": [],
    "pinterest": ['pin', 'пин', 'пинтерест'],
    "play": ['p', 'играй'],
    "record_voice": ['запиши', 'запись', 'recordme', 'голосзапись'],
    "reload": ['rl', 'перезагрузить'],
    "reload_all": ['reloadall', 'перезагрузитьвсе'],
    "restart": ['рестарт', 'reboot', 'rs'],
    "resume": ['продолжить', 'res'],
    "show_aliases": ['алиасы', 'aliases', 'allaliases'],
    "skip": ['next', 's', 'пропустить'],
    "start_listen": ['listen', 'слушай', 'голос', 'включиголос', 'stt'],
    "stop_listen": ['stoplisten', 'стопголос', 'выключиголос'],
    "structure": ['структура', 'project', 'tree'],
    "tech": ['тех', 'обслуживание', 'maintenance', 'техрежим'],
    "tts": ['скажи', 'произнеси'],
    "unload": ['выгрузить'],
    "unmute": ['размут'],
    "userinfo": ['id', 'userid', 'uid'],
    "vkphoto": ['вкфото', 'вк', 'randvk', 'фото', 'вкрандом'],
}

# ====================== СТРУКТУРА КАТЕГОРИЙ ======================
COMMAND_CATEGORIES = {
    "BASIC": ["ping", "hello", "about", "clear", "userinfo", "myid", "show_aliases", "botstat", "tech"],
    "FORZA": ["forza_status", "forzaprofile"],
    "VOICE AI": ["join_voice", "leave_voice", "tts"],
    "VOICE STT": ["start_listen", "stop_listen", "record_voice"],
    "CUSTOM ROLE": ["createrole", "listcustomroles"],
    "FUN": ["meme", "eightball"],
    "MODERATION": ["ban", "kick", "mute", "unmute"],
    "PHOTO": ["pinterest", "vkphoto"],
    "AUDIO": ["play", "skip", "pause", "resume", "leave"],
    "RELOAD": ["reload", "restart", "load", "unload", "reload_all"],
}

# Отображение для интерфейса
CATEGORY_DISPLAY = {
    "BASIC": "🌍 basic",
    "FORZA": "🏎️ forza",
    "VOICE AI": "🎙️ voice_ai",
    "VOICE STT": "🎤 voice_stt",
    "CUSTOM ROLE": "👑 custom_role",
    "FUN": "🎲 fun",
    "MODERATION": "🛡️ moderation",
    "PHOTO": "🖼️ photo",
    "AUDIO": "🎵 audio",
    "RELOAD": "🔄 reload",
}

def save_aliases(new_aliases_dict: dict):
    """Сохраняет обновлённый словарь алиасов"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "aliases.py")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        start_idx = None
        end_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("COMMAND_ALIASES = {"):
                start_idx = i
            if start_idx is not None and line.strip() == "}":
                end_idx = i
                break

        if start_idx is None or end_idx is None:
            raise Exception("Не удалось найти COMMAND_ALIASES")

        new_lines = ["COMMAND_ALIASES = {\n"]
        for cmd in sorted(new_aliases_dict.keys()):
            aliases = new_aliases_dict[cmd]
            aliases_str = str(aliases) if aliases else "[]"
            new_lines.append(f'    "{cmd}": {aliases_str},\n')
        new_lines.append("}\n")

        updated_lines = lines[:start_idx] + new_lines + lines[end_idx + 1:]

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        import utils.aliases
        importlib.reload(utils.aliases)

        return True, "✅ Алиасы успешно сохранены и применены"

    except Exception as e:
        return False, f"❌ Ошибка сохранения: {e}"


def get_aliases(command_name: str) -> list:
    return COMMAND_ALIASES.get(command_name, [])


def get_all_aliases_formatted() -> str:
    """Возвращает красивый текст со всеми алиасами"""
    lines = ["**Все алиасы команд Мафани:**\n```python"]
    
    for category, cmds in [
        ("BASIC", ["ping", "hello", "about", "clear", "userinfo", "myid", "show_aliases", "botstat", "tech"]),
        ("FORZA", ["forza_status", "forzaprofile"]),
        ("VOICE AI", ["join_voice", "leave_voice", "tts"]),
        ("VOICE STT", ["start_listen", "stop_listen", "record_voice"]),
        ("CUSTOM ROLE", ["createrole", "listcustomroles"]),
        ("FUN", ["meme", "eightball"]),
        ("HELP", ["helpimage"]),
        ("MODERATION", ["ban", "kick", "mute", "unmute"]),
        ("PHOTO", ["pinterest", "vkphoto"]),
        ("RELOAD", ["reload", "restart", "load", "unload", "reload_all"]),
        ("STRUCTURE", ["structure"]),
        ("AUDIO", ["play", "skip", "pause", "resume", "leave"]),
    ]:
        lines.append(f"\n# ====================== {category} ======================")
        for cmd in cmds:
            aliases = COMMAND_ALIASES.get(cmd, [])
            aliases_str = str(aliases) if aliases else "[]"
            lines.append(f'    "{cmd}": {aliases_str},')
    
    lines.append("\n```")
    return "\n".join(lines)