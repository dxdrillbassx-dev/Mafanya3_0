# utils/aliases.py

COMMAND_ALIASES = {
    # ====================== BASIC ======================
    "ping": [],
    "hello": ["привет"],
    "about": ["бот", "инфо"],
    "clear": ["очистить", "purge"],
    "userinfo": ["id", "userid", "uid"],
    "myid": ["мойid", "мойид"],
    "show_aliases": ["алиасы", "aliases", "allaliases"],
    "botstat": ["стат", "стата", "статистика", "status"],
    "tech": ["тех", "обслуживание", "maintenance", "техрежим"],

    # ====================== FORZA ======================
    "forza_status": ["forza", "форза", "форца"],
    "forzaprofile": ["forzadash", "fd", "dash", "fprofile", "forzainfo", "finfo", "форзапрофиль", "профильфорза"],

    # ====================== VOICE AI ======================
    "join_voice": ["join", "зайди", "voice"],
    "leave_voice": ["выйди", "dis", "leaveai"],
    "tts": ["скажи", "произнеси"],

    # ====================== VOICE STT ======================
    "start_listen": ["listen", "слушай", "голос", "включиголос", "stt"],
    "stop_listen": ["stoplisten", "стопголос", "выключиголос"],
    "record_voice": ["запиши", "запись", "recordme", "голосзапись"], 

    # ====================== CUSTOM ROLE ======================
    "createrole": ["личная", "мояроль", "своя"],
    "listcustomroles": ["личные", "все_личные", "adminroles"],

    # ====================== FUN ======================
    "meme": ["мем"],
    "eightball": ["8ball", "шар", "магическийшар"],

    # ====================== HELP ======================
    "helpimage": ["helpimg", "меню", "команды", "himg", "help"],

    # ====================== MODERATION ======================
    "ban": ["бан"],
    "kick": ["кик"],
    "mute": ["мут", "timeout"],
    "unmute": ["размут"],

    # ====================== PHOTO ======================
    "pinterest": ["pin", "пин", "пинтерест"],
    "vkphoto": ["вкфото", "вк", "randvk", "фото", "вкрандом"],

    # ====================== RELOAD ======================
    "reload": ["rl", "перезагрузить"],
    "restart": ["рестарт", "reboot", "rs"],
    "load": ["загрузить"],
    "unload": ["выгрузить"],
    "reload_all": ["reloadall", "перезагрузитьвсе"],

    # ====================== STRUCTURE ======================
    "structure": ["структура", "project", "tree"],

    # ====================== AUDIO ======================
    "play": ["p", "играй"],
    "skip": ["next", "s", "пропустить"],
    "pause": ["пауза"],
    "resume": ["продолжить", "res"],
    "leave": ["dc", "выйти", "aleave"],
}


def get_aliases(command_name: str) -> list:
    """Возвращает список алиасов для команды"""
    return COMMAND_ALIASES.get(command_name, [])


def get_all_aliases_formatted() -> str:
    """Возвращает красивый текст со всеми алиасами"""
    lines = ["**Все алиасы команд Мафани:**\n```python"]
    
    for category, cmds in [
        ("BASIC", ["ping", "hello", "about", "clear", "userinfo", "myid", "show_aliases", "botstat"]),
        ("FORZA", ["forza_status", "forzaprofile"]),
        ("VOICE AI", ["join_voice", "leave_voice", "tts"]),
        ("CUSTOM ROLE", ["createrole", "listcustomroles"]),
        ("FUN", ["meme", "eightball"]),
        ("HELP", ["helpimage"]),
        ("MODERATION", ["ban", "kick", "mute", "unmute"]),
        ("PHOTO", ["pinterest", "vkphoto"]),
        ("RELOAD", ["reload", "load", "unload", "reload_all"]),
        ("STRUCTURE", ["structure"]),
        ("AUDIO", ["play", "skip", "pause", "resume", "leave"]),
    ]:
        lines.append(f"\n# ====================== {category} ======================")
        for cmd in cmds:
            aliases = COMMAND_ALIASES.get(cmd, [])
            aliases_str = str(aliases) if aliases else "[]"
            lines.append(f'    "{cmd}": {aliases_str},')
    
    lines.append("```")
    return "\n".join(lines)