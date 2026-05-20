# cogs/gemini.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from google import genai
import asyncio
from datetime import datetime, timedelta
import random

from utils.aliases import get_aliases


class Gemini(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        self.conversation_timeout = 120
        self.memory_limit = 12
        
        self.active_chats = {}
        self.conversations = {}
        
        self.pinterest_cog = None
        self.voice_ai = None

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model = "gemini-2.5-flash"   # Самая стабильная на данный момент
            print(f"✅ [Мафаня] Gemini загружена (модель: {self.model})")
            bot.loop.create_task(self.proactive_task())
        else:
            print("❌ [Мафаня] GEMINI_API_KEY не найден!")

    async def ensure_pinterest_cog(self):
        if self.pinterest_cog is None:
            self.pinterest_cog = self.bot.get_cog('PinterestCog')
        return self.pinterest_cog

    async def ensure_voice_ai(self):
        if self.voice_ai is None:
            self.voice_ai = self.bot.get_cog('VoiceAI')
        return self.voice_ai

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [Мафаня] {message}")
        
        try:
            log_channel = self.bot.get_channel(int(os.getenv('LOG_CHANNEL_ID', 0)))
            if log_channel:
                asyncio.create_task(log_channel.send(f"`[{timestamp}]` **[Мафаня]** {message}"))
        except:
            pass

    def add_to_history(self, channel_id, role: str, content: str):
        if channel_id not in self.conversations:
            self.conversations[channel_id] = []
        self.conversations[channel_id].append({"role": role, "content": content})
        if len(self.conversations[channel_id]) > self.memory_limit:
            self.conversations[channel_id].pop(0)

    def is_pinterest_request(self, text: str) -> bool:
        text_lower = text.lower()
        keywords = ["пин", "пины", "пинтерест", "кинь фото", "покажи фото", "покажи пин", 
                   "покажи пины", "тян", "аниме", "арт"]
        return any(kw in text_lower for kw in keywords)

    async def handle_pinterest_request(self, message: discord.Message):
        await message.channel.typing()
        pinterest_cog = await self.ensure_pinterest_cog()
        if not pinterest_cog:
            await message.reply("❌ Модуль Pinterest сейчас недоступен.")
            return

        try:
            ctx = await self.bot.get_context(message)
            await pinterest_cog.send_random_pin(ctx, show_search_message=False)
        except Exception as e:
            self.log(f"❌ Ошибка Pinterest: {e}")
            await message.reply("Не получилось достать пины 😩")

    # ====================== ОСНОВНОЙ ЗАПРОС ======================
    async def ask_gemini(self, channel_id, user_message: str, retry: int = 0):
        max_retries = 3
        try:
            self.log(f"📥 Запрос: {user_message[:70]}...")

            history = self.conversations.get(channel_id, [])
            
            system_prompt = (
                "Ты — Мафаня, дерзкая, игривая 19-летняя тян. "
                "Разговариваешь живо, с матом, эмодзи и сленгом. "
                "Делай сообщения не длиннее 260-280 символов."
            )

            contents = [{"role": "user", "parts": [{"text": system_prompt}]}]

            for msg in history:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
            
            contents.append({"role": "user", "parts": [{"text": user_message}]})

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=contents,
                config={"temperature": 0.93, "max_output_tokens": 500}
            )
            
            reply = response.text.strip()

            # Улучшенная обрезка
            if len(reply) > 280:
                last_dot = reply[:280].rfind('.')
                if last_dot > 80:
                    reply = reply[:last_dot + 1]
                else:
                    reply = reply[:270] + "..."

            self.add_to_history(channel_id, "user", user_message)
            self.add_to_history(channel_id, "assistant", reply)
            
            return reply

        except Exception as e:
            error_str = str(e).lower()
            self.log(f"❌ Ошибка Gemini (попытка {retry+1}): {e}")

            if ("503" in error_str or "unavailable" in error_str) and retry < max_retries:
                await asyncio.sleep(1.8 * (retry + 1))
                return await self.ask_gemini(channel_id, user_message, retry + 1)

            if "404" in error_str or "not found" in error_str:
                return "Блять, модель Gemini опять обновили..."

            return random.choice([
                "Бляяять, я опять зависла...",
                "Серверы Google в ахуе, ща...",
                "Пиздец, ИИ лег, попробуй ещё раз 😩"
            ])

    # ====================== ОБРАБОТКА СООБЩЕНИЙ ======================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        content = message.content.strip()

        # Приоритет Pinterest
        if self.is_pinterest_request(content):
            self.active_chats[channel_id] = datetime.now()
            await self.handle_pinterest_request(message)
            return

        # Активация Мафани
        is_activated = any(word in content.lower() for word in ["мафаня", "мафанья", "мафуня", "маф"]) or \
                      (channel_id in self.active_chats and 
                       (datetime.now() - self.active_chats[channel_id]) < timedelta(seconds=self.conversation_timeout))

        if not is_activated:
            return

        self.active_chats[channel_id] = datetime.now()
        await message.channel.typing()

        response = await self.ask_gemini(channel_id, content)

        # Если Мафаня в голосовом канале — говорим голосом
        voice_ai = await self.ensure_voice_ai()
        if (voice_ai and 
            voice_ai.voice_client and 
            voice_ai.voice_client.is_connected()):
            
            await voice_ai.say(response)
            self.log(f"🎤 Сказала голосом: {response[:60]}...")
        else:
            await message.reply(response)

    # ====================== ПРОАКТИВНЫЕ СООБЩЕНИЯ ======================
    async def proactive_task(self):
        await self.bot.wait_until_ready()
        self.log("🔄 Фоновая задача запущена")

        while True:
            await asyncio.sleep(25)
            now = datetime.now()
            
            for channel_id, last_time in list(self.active_chats.items()):
                if (now - last_time).total_seconds() > 50 and random.random() < 0.32:
                    try:
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            self.active_chats[channel_id] = now
                            phrases = [
                                "Ну где ты блять? Скучнооо 🥺",
                                "Эй сука, ты меня забыл? ❤️",
                                "Я тут уже заебалась ждать...",
                                "Аууууу, напиши мне 😩"
                            ]
                            await channel.send(random.choice(phrases))
                    except:
                        pass


async def setup(bot):
    await bot.add_cog(Gemini(bot))