import discord
import os
import datetime
import random
import asyncio
import signal
import sys
import json

from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import Select, View
from utils.module_descriptions import MODULE_DESCRIPTIONS

load_dotenv()

TOKEN = os.getenv('TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID', 0))
ROLE_ID = int(os.getenv('ROLE_ID', 0))
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', 0))
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID', LOG_CHANNEL_ID))

# AI Ключи
XAI_API_KEY = os.getenv('XAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Другие сервисы
PINTEREST_EMAIL = os.getenv('PINTEREST_EMAIL')
PINTEREST_PASSWORD = os.getenv('PINTEREST_PASSWORD')
VK_TOKEN = os.getenv('VK_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ====================== ЦЕНТРАЛИЗОВАННЫЕ СООБЩЕНИЯ ======================
BOT_MESSAGES = {}

def get_messages_path():
    """Определяет правильный путь к bot_messages.json"""
    # Если бот запущен из корня проекта
    base_path = os.path.dirname(os.path.abspath(__file__))
    messages_path = os.path.join(base_path, "data", "bot_messages.json")
    
    if os.path.exists(messages_path):
        return messages_path
    
    # Если запущен из launcher (запасной вариант)
    launcher_path = os.path.join(base_path, "launcher", "data", "bot_messages.json")
    if os.path.exists(launcher_path):
        return launcher_path
    
    # Если ничего не найдено — создаём в data
    data_dir = os.path.join(base_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "bot_messages.json")


def load_bot_messages():
    """Загружает все сообщения из JSON"""
    global BOT_MESSAGES
    messages_path = get_messages_path()
    
    try:
        if os.path.exists(messages_path):
            with open(messages_path, "r", encoding="utf-8") as f:
                BOT_MESSAGES = json.load(f)
            print(f"✅ bot_messages.json успешно загружен: {messages_path}")
        else:
            print(f"❌ bot_messages.json не найден: {messages_path}")
            BOT_MESSAGES = {}
    except Exception as e:
        print(f"❌ Ошибка загрузки bot_messages.json: {e}")
        BOT_MESSAGES = {}


def get_message(section: str, key: str, default: str = "", **kwargs):
    """Универсальная функция получения сообщения с поддержкой вариативности (списки)"""
    if not BOT_MESSAGES:
        return default

    data = BOT_MESSAGES.get(section, {}).get(key, default)

    # === НОВАЯ ЛОГИКА: поддержка списка вариантов ===
    if isinstance(data, list) and data:
        text = random.choice(data)  # рандомный выбор
    else:
        text = data  # обычная строка

    # Применяем шаблон (error/success и т.д.)
    template_key = "error" if section == "errors" else section
    template = BOT_MESSAGES.get("templates", {}).get(template_key)
    
    if template and text:
        text = template.format(text=text)

    # Подставляем переменные ({member}, {id} и т.д.)
    if text and kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass

    return text or default


# ====================== ГЛОБАЛЬНЫЙ СПИСОК ОТКЛЮЧЁННЫХ КОМАНД ======================
DISABLED_COMMANDS = set()

def load_disabled_commands():
    global DISABLED_COMMANDS
    try:
        if os.path.exists("disabled_commands.json"):
            with open("disabled_commands.json", "r", encoding="utf-8") as f:
                DISABLED_COMMANDS = set(json.load(f))
            print(f"✅ Загружено отключённых команд: {len(DISABLED_COMMANDS)}")
        else:
            print("ℹ️ Файл disabled_commands.json не найден")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки disabled_commands.json: {e}")


# ====================== ФИКС КОДИРОВКИ ======================
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


# ==================== ОТПРАВКА ЛОГОВ ====================
async def send_log(message: str):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            await channel.send(f"`[{timestamp}]` {message}")
        except:
            pass


# ==================== GRACEFUL SHUTDOWN ====================
async def graceful_shutdown():
    print("\n🔴 Получен сигнал завершения. Завершаем работу...")
    await asyncio.sleep(1)
    try:
        await bot.close()
    except:
        pass
    print("✅ Бот успешно выключен")


def handle_signal(sig, frame):
    print(f"\n⚠️  Получен сигнал {sig}. Запускаю graceful shutdown...")
    asyncio.create_task(graceful_shutdown())


signal.signal(signal.SIGINT, handle_signal)
if sys.platform != "win32":
    signal.signal(signal.SIGTERM, handle_signal)


@bot.check
async def is_command_enabled(ctx):
    if ctx.command and ctx.command.name in DISABLED_COMMANDS:
        try:
            await ctx.send(get_message("errors", "maintenance", "Команда отключена"), delete_after=8)
        except:
            pass
        return False
    return True


@bot.event
async def on_ready():
    if hasattr(bot, '_ready_fired') and bot._ready_fired:
        return  # ← Защита от многократного запуска
    
    bot._ready_fired = True

    print("\n" + "="*65)
    print(f"✅ Бот {bot.user} успешно запущен!")
    print("="*65)

    check_env_variables()
    load_bot_messages()

    # ====================== ЗАГРУЗКА МОДУЛЕЙ ======================
    print("\n🔄 Загрузка модулей...")
    successful = []
    failed = []

    for root, dirs, files in os.walk('./cogs'):
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('__'):
                rel_path = os.path.relpath(os.path.join(root, filename), './cogs')
                module_path = rel_path.replace(os.sep, '.')[:-3]
                try:
                    await bot.load_extension(f'cogs.{module_path}')
                    successful.append(module_path)
                    print(f"   ✅ {module_path}")
                except Exception as e:
                    failed.append(f"{module_path} — {e}")
                    print(f"   ❌ {module_path}")

    total = len(successful) + len(failed)
    print(f"\n🎉 Загрузка модулей завершена! Успешно: {len(successful)}/{total}")
    
    await send_log(get_message("logs", "bot_ready", f"Бот готов. Серверов: {len(bot.guilds)}", 
                              guilds=len(bot.guilds)))

    # ====================== EMBED ======================
    embed = discord.Embed(
        title=get_message("status", "bot_started", "✅ Бот успешно запущен"),
        description=f"**{bot.user}** | Серверов: **{len(bot.guilds)}**",
        color=0xFF69B4,
        timestamp=datetime.datetime.now(datetime.UTC)
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    if successful:
        modules_list = "\n".join([f"`• {m}`" for m in sorted(successful)])
        embed.add_field(
            name=get_message("status", "modules_loaded", f"📦 Загружено модулей: {len(successful)}/{total}"),
            value=modules_list, 
            inline=False
        )

    env_text = get_env_status_text()
    embed.add_field(name="🔑 Проверка .env", value=env_text, inline=False)

    if failed:
        embed.add_field(name="❌ Ошибки загрузки", value="```" + "\n".join(failed[:10]) + "```", inline=False)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        try:
            await log_channel.send(embed=embed)
        except:
            pass

    print("\n" + "="*65)
    print("Mafanya 3.0 полностью готова к работе!")
    print("="*65)

# ==================== Остальной код без изменений ====================
def get_env_status_text() -> str:
    checks = {
        "TOKEN": bool(TOKEN and len(TOKEN) > 50),
        "OWNER_ID": OWNER_ID != 0,
        "ROLE_ID": ROLE_ID != 0,
        "LOG_CHANNEL_ID": LOG_CHANNEL_ID != 0,
        "WELCOME_CHANNEL_ID": WELCOME_CHANNEL_ID != 0,
        "XAI_API_KEY": bool(XAI_API_KEY and XAI_API_KEY.startswith('xai-')),
        "GEMINI_API_KEY": bool(GEMINI_API_KEY and GEMINI_API_KEY.startswith('AIza')),
        "PINTEREST_EMAIL": bool(PINTEREST_EMAIL),
        "PINTEREST_PASSWORD": bool(PINTEREST_PASSWORD),
        "VK_TOKEN": bool(VK_TOKEN and VK_TOKEN.startswith('vk1.a.')),
    }

    lines = [f"`• {key}` → **{'OK' if status else 'НЕ НАЙДЕН'}**" 
             for key, status in checks.items()]
    return "\n".join(lines)


def check_env_variables():
    print("\n🔑 Проверка переменных окружения (.env):")
    print("-" * 55)
    print("-" * 55)


@bot.event
async def on_member_join(member):
    role = member.guild.get_role(ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
            log_msg = get_message("logs", "role_given", "Выдал роль **{role}** → {member} (`{id}`)", 
                                role=role.name, member=member.mention, id=member.id)
            await send_log(log_msg)
        except Exception as e:
            error_msg = get_message("errors", "role_give_failed", "Не удалось выдать роль")
            await send_log(f"{error_msg} {member.mention}: {e}")

    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        welcome_msg = get_message("welcome", "message", 
                                 "🎉 **{member}** присоединился к серверу! Добро пожаловать!", 
                                 member=member.mention)
        await welcome_channel.send(welcome_msg)


@bot.event
async def on_member_remove(member):
    log_msg = get_message("logs", "member_leave", "{member} (`{id}`) покинул сервер", 
                         member=member, id=member.id)
    await send_log(log_msg)


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        msg = get_message("logs", "voice_join", "{member} зашёл в **{channel}**", 
                         member=member.mention, channel=after.channel.name)
        await send_log(msg)
    elif before.channel is not None and after.channel is None:
        msg = get_message("logs", "voice_leave", "{member} вышел из голосового канала", 
                         member=member.mention)
        await send_log(msg)


@bot.event
async def on_command_completion(ctx):
    try:
        dont_delete = ["helpimage", "structure", "vkphoto", "ping", "botstat", "vktest"]
        if ctx.command and ctx.command.name not in dont_delete:
            await ctx.message.delete()
    except:
        pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        try:
            await ctx.message.delete()
        except:
            pass
        funny_list = BOT_MESSAGES.get("funny_responses", ["Хуйню какую-то пишешь, братан 😂"])
        response = random.choice(funny_list)
        await ctx.send(response, delete_after=8)

    elif isinstance(error, commands.MissingRequiredArgument):
        msg = get_message("errors", "missing_arguments", "Не хватает аргументов команды")
        await ctx.send(msg, delete_after=10)
    elif isinstance(error, commands.MissingPermissions):
        msg = get_message("errors", "no_permissions", "У тебя недостаточно прав")
        await ctx.send(msg, delete_after=10)
    else:
        print(f"Command error: {error}")


# ==================== ЗАПУСК БОТА ====================
print("[*] Запуск бота Mafanya 3.0...")
load_disabled_commands()
load_bot_messages()

try:
    import launcher.shared as shared
    shared.bot_instance = bot
    print("✅ Бот успешно передан в shared модуль лаунчера")
except Exception as e:
    print(f"⚠️ Не удалось сохранить bot в shared: {e}")

bot.run(TOKEN)