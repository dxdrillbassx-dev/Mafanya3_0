import discord
import os
import datetime
import random
import asyncio
import signal
import sys

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
STATUS_CHANNEL_ID = int(os.getenv('STATUS_CHANNEL_ID', 0))

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
last_status_change = None


def get_env_status_text() -> str:
    """Компактный вывод .env в одну строку"""
    checks = {
        "TOKEN": bool(TOKEN and len(TOKEN) > 50),
        "OWNER_ID": OWNER_ID != 0,
        "ROLE_ID": ROLE_ID != 0,
        "LOG_CHANNEL_ID": LOG_CHANNEL_ID != 0,
        "WELCOME_CHANNEL_ID": WELCOME_CHANNEL_ID != 0,
        "STATUS_CHANNEL_ID": STATUS_CHANNEL_ID != 0,
        "XAI_API_KEY": bool(XAI_API_KEY and XAI_API_KEY.startswith('xai-')),
        "GEMINI_API_KEY": bool(GEMINI_API_KEY and GEMINI_API_KEY.startswith('AIza')),
        "PINTEREST_EMAIL": bool(PINTEREST_EMAIL),
        "PINTEREST_PASSWORD": bool(PINTEREST_PASSWORD),
        "VK_TOKEN": bool(VK_TOKEN and VK_TOKEN.startswith('vk1.a.')),
    }

    lines = [f"`• {key}` → **{'OK' if status else 'НЕ НАЙДЕН'}**" 
             for key, status in checks.items()]
    
    return "\n".join(lines)


# ==================== ОТПРАВКА ЛОГОВ ====================
async def send_log(message: str):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            await channel.send(f"`[{timestamp}]` {message}")
        except:
            pass


# ==================== STATUS CHANNEL ====================
async def set_bot_status(online: bool):
    """Меняет название канала с максимальной защитой от rate limit"""
    if not STATUS_CHANNEL_ID:
        return
    
    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if not channel:
        return

    try:
        new_name = "🟢 Mafanya 3.0" if online else "🔴 Mafanya 3.0"
        
        if channel.name == new_name:
            print(f"Статус уже {new_name} — пропускаем")
            return

        await channel.edit(name=new_name)
        await send_log(f"📛 Статус канала изменён → **{new_name}**")
        print(f"✅ Статус успешно изменён на: {new_name}")

    except discord.HTTPException as e:
        if e.status == 429:                    # Rate Limit
            retry_after = getattr(e, 'retry_after', 120)
            print(f"⚠️ RATE LIMIT! Пропускаем смену названия канала (ждать {retry_after:.0f} сек)")
            await send_log(f"⚠️ Rate Limit при смене статуса. Изменение пропущено.")
            # Никаких await sleep — сразу выходим
        else:
            print(f"❌ HTTP ошибка при смене названия: {e.status} {e.text}")
    except Exception as e:
        print(f"❌ Неизвестная ошибка при смене статуса канала: {e}")


# ==================== GRACEFUL SHUTDOWN ====================
async def graceful_shutdown():
    """Корректное выключение бота с изменением статуса"""
    print("\n🔴 Получен сигнал завершения. Меняю статус канала на красный...")
    await set_bot_status(online=False)
    await asyncio.sleep(1.5)  # даём время на изменение названия
    
    try:
        await bot.close()
    except:
        pass
    print("✅ Бот успешно выключен")


def handle_signal(sig, frame):
    """Обработчик Ctrl+C и других сигналов"""
    print(f"\n⚠️  Получен сигнал {sig}. Запускаю graceful shutdown...")
    asyncio.create_task(graceful_shutdown())


# Регистрируем обработчики сигналов
signal.signal(signal.SIGINT, handle_signal)   # Ctrl + C
if sys.platform != "win32":
    signal.signal(signal.SIGTERM, handle_signal)


@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.now(datetime.UTC)
    
    print("\n" + "="*65)
    print(f"✅ Бот {bot.user} успешно запущен!")
    print("="*65)

    check_env_variables()

    # ====================== СТАТУС КАНАЛА ======================
    try:
        await asyncio.wait_for(set_bot_status(online=True), timeout=8.0)  # максимум 8 секунд
    except asyncio.TimeoutError:
        print("⏳ Смена статуса канала превысила лимит времени — пропущено")
    except Exception as e:
        print(f"❌ Ошибка смены статуса: {e}")

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
    print(f"\n🎉 Загрузка модулей завершена!")
    print(f"   ✅ Успешно: {len(successful)}/{total}")

    # ====================== EMBED + ИНТЕРАКТИВНЫЙ DROPDOWN ======================
    embed = discord.Embed(
        title="✅ Бот успешно запущен",
        description=f"**{bot.user}** | Серверов: **{len(bot.guilds)}**",
        color=0xFF69B4,
        timestamp=datetime.datetime.now(datetime.UTC)
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    # Левая колонка — список модулей
    if successful:
        modules_list = "\n".join([f"`• {m}`" for m in sorted(successful)])
        embed.add_field(
            name=f"📦 Загружено модулей: {len(successful)}/{total}", 
            value=modules_list, 
            inline=True
        )

    # Правая колонка — .env
    env_text = get_env_status_text()
    embed.add_field(
        name="🔑 Проверка .env", 
        value=env_text, 
        inline=True
    )

    if failed:
        embed.add_field(
            name="❌ Ошибки загрузки", 
            value="```" + "\n".join(failed[:12]) + "```", 
            inline=False
        )

    embed.set_footer(text="Нажми на выпадающий список ниже, чтобы посмотреть описание модуля")

    # ==================== DROPDOWN С ОПИСАНИЯМИ ====================
    class ModuleSelect(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)  # активно 5 минут

            options = []
            for mod in sorted(successful):
                # Берём описание из словаря, если нет — стандартный текст
                desc = MODULE_DESCRIPTIONS.get(mod, MODULE_DESCRIPTIONS.get(mod.split('.')[-1], "Описание модуля пока отсутствует."))
                options.append(discord.SelectOption(
                    label=mod,
                    value=mod,
                    description=desc[:100] if desc else "Нет описания"
                ))

            select = discord.ui.Select(
                placeholder="🔍 Выбери модуль для просмотра описания...",
                options=options,
                min_values=1,
                max_values=1
            )
            select.callback = self.select_callback
            self.add_item(select)

        async def select_callback(self, interaction: discord.Interaction):
            module_name = interaction.data['values'][0]
            desc = MODULE_DESCRIPTIONS.get(module_name, 
                  MODULE_DESCRIPTIONS.get(module_name.split('.')[-1], "Описание для этого модуля ещё не добавлено."))
            
            await interaction.response.send_message(
                f"**📄 Модуль:** `{module_name}`\n\n{desc}",
                ephemeral=True  # видно только тому, кто нажал
            )

    # Отправка эмбеда с выпадающим списком
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        try:
            view = ModuleSelect()
            await log_channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"❌ Не удалось отправить embed с dropdown: {e}")
            # fallback без dropdown
            await log_channel.send(embed=embed)

    print("\n" + "="*65)
    print("🚀 Mafanya 3.0 полностью готова к работе!")
    print("="*65)


def check_env_variables():
    """Вывод в консоль"""
    print("\n🔑 Проверка переменных окружения (.env):")
    print("-" * 55)
    
    checks = {
        "TOKEN": bool(TOKEN and len(TOKEN) > 50),
        "OWNER_ID": OWNER_ID != 0,
        "ROLE_ID": ROLE_ID != 0,
        "LOG_CHANNEL_ID": LOG_CHANNEL_ID != 0,
        "WELCOME_CHANNEL_ID": WELCOME_CHANNEL_ID != 0,
        "STATUS_CHANNEL_ID": STATUS_CHANNEL_ID != 0,
        "XAI_API_KEY": bool(XAI_API_KEY and XAI_API_KEY.startswith('xai-')),
        "GEMINI_API_KEY": bool(GEMINI_API_KEY and GEMINI_API_KEY.startswith('AIza')),
        "PINTEREST_EMAIL": bool(PINTEREST_EMAIL),
        "PINTEREST_PASSWORD": bool(PINTEREST_PASSWORD),
        "VK_TOKEN": bool(VK_TOKEN and VK_TOKEN.startswith('vk1.a.')),
    }

    for key, status in checks.items():
        icon = "✅" if status else "❌"
        value = "OK" if status else "НЕ НАЙДЕН / НЕВЕРНЫЙ"
        print(f"   {icon} {key:22} → {value}")
    
    missing = [k for k, v in checks.items() if not v]
    if missing:
        print(f"\n⚠️  ВНИМАНИЕ! Проблемы с ключами: {', '.join(missing)}")
    else:
        print("\n🎉 Все важные ключи .env загружены успешно!")
    print("-" * 55)


# ==================== СОБЫТИЯ ====================
@bot.event
async def on_member_join(member):
    role = member.guild.get_role(ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
            await send_log(f"✅ Выдал роль **{role.name}** → {member.mention} (`{member.id}`)")
        except Exception as e:
            await send_log(f"❌ Не удалось выдать роль {member.mention}: {e}")

    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        await welcome_channel.send(f"🎉 **{member.mention}** присоединился к серверу! Добро пожаловать!")


@bot.event
async def on_member_remove(member):
    await send_log(f"👋 {member} (`{member.id}`) покинул сервер")


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        await send_log(f"🔊 {member.mention} зашёл в **{after.channel.name}**")
    elif before.channel is not None and after.channel is None:
        await send_log(f"🔇 {member.mention} вышел из голосового канала")


FUNNY_RESPONSES = [
    "Хуйню какую-то пишешь, братан 😂",
    "Я хуй знает чё ты от меня хочешь, серьёзно",
    "Команда не найдена, иди нахуй с такими запросами",
    "Ты серьёзно? Такой команды нет, долбоёб",
    "Не понимаю тебя, пидор. Пиши нормальные команды",
    "🤡 Ты чё, ёбанутый? Такой команды нет",
    "Бля, опять хуйню ввёл...",
    "Мамку свою так командуй, а не меня",
    "Я тебе не ебаный гугл, учи команды",
    "😂😂😂 пиши !helpimg, мудила"
]


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
        response = random.choice(FUNNY_RESPONSES)
        await ctx.send(response, delete_after=8)

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Не хватает аргументов команды.", delete_after=10)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У тебя недостаточно прав для этой команды.", delete_after=10)
    else:
        print(f"Command error: {error}")


# ==================== ЗАПУСК БОТА ====================
print("🚀 Запуск бота Mafanya 3.0...")
bot.run(TOKEN)