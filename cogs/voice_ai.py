# cogs/voice_ai.py
import discord
from discord.ext import commands
import asyncio
import os
import random
import re
import torch
import soundfile as sf

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт


class VoiceAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.current_channel = None
        self.is_speaking = False
        self.temp_dir = "temp_tts"
        os.makedirs(self.temp_dir, exist_ok=True)

        # Загрузка Silero
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(get_message("voice_ai", "silero_loading", device=self.device))

        # Загружаем модель
        self.model, self.example_text = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='ru',
            speaker='v4_ru'
        )
        self.model.to(self.device)
        print(get_message("voice_ai", "silero_loaded"))

    def clean_text_for_tts(self, text: str) -> str:
        """Очистка текста"""
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
        replacements = {
            "❤️": "сердце",
            "🥺": "",
            "😩": "блин",
            "😵‍💫": "ой",
            "...": ". ",
            "…": ". ",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return re.sub(r'\s+', ' ', text).strip() or "Ммм?"

    # ====================== КОМАНДЫ ======================
    @commands.command(aliases=get_aliases("join_voice"))
    async def join_voice(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(get_message("voice_ai", "not_in_voice"))

        try:
            self.voice_client = await ctx.author.voice.channel.connect()
            self.current_channel = ctx.channel
            await ctx.send(
                get_message("voice_ai", "join_success", channel=ctx.author.voice.channel.name)
            )
            await asyncio.sleep(0.5)
            await self.say(get_message("voice_ai", "join_greeting"))
        except Exception as e:
            await ctx.send(get_message("voice_ai", "join_error", error=str(e)))

    @commands.command(aliases=get_aliases("leave_voice"))
    async def leave_voice(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            self.current_channel = None
            await ctx.send(get_message("voice_ai", "leave_success"))
        else:
            await ctx.send(get_message("voice_ai", "not_in_voice_leave"))

    # ====================== ОЗВУЧКА ======================
    async def say(self, text: str):
        if not self.voice_client or self.is_speaking:
            return

        try:
            self.is_speaking = True
            clean_text = self.clean_text_for_tts(text)

            filename = f"{self.temp_dir}/mafanya_{random.randint(10000,99999)}.wav"

            audio = self.model.apply_tts(
                text=clean_text[:450],
                speaker="baya",
                sample_rate=48000,
                put_accent=True,
                put_yo=True
            )

            sf.write(filename, audio.numpy(), 48000)

            if self.voice_client.is_playing():
                self.voice_client.stop()

            source = discord.FFmpegPCMAudio(filename)
            self.voice_client.play(source, after=lambda e: self.cleanup(filename))

            print(f"[VoiceAI] 🎤 Сказала: {clean_text[:70]}...")

        except Exception as e:
            print(f"[TTS] Ошибка: {e}")
            if self.current_channel:
                await self.current_channel.send(
                    get_message("voice_ai", "tts_error"), 
                    delete_after=5
                )
        finally:
            self.is_speaking = False

    def cleanup(self, filename):
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

    # ====================== РЕАКЦИЯ НА СООБЩЕНИЯ ======================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.voice_client or not self.current_channel:
            return
        if message.channel != self.current_channel:
            return

        content = message.content.lower()
        if any(word in content for word in ["мафаня", "мафанья", "мафуня", "маф"]):
            text = message.content
            for word in ["мафаня", "мафанья", "мафуня", "маф"]:
                text = text.replace(word, "").strip(",.!? ")

            if not text:
                text = "Да, мой хороший?"

            response = await self.get_ai_response(text)
            await self.say(response)

    async def get_ai_response(self, text: str):
        gemini = self.bot.get_cog('Gemini')
        if gemini:
            try:
                return await gemini.ask_gemini(self.current_channel.id, text)
            except:
                pass
        return random.choice(get_message("voice_ai", "ai_fallback"))


async def setup(bot):
    await bot.add_cog(VoiceAI(bot))