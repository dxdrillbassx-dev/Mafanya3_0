# cogs/voice_stt.py
import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт

# Для записи голоса
from discord.ext import voice_recv


class VoiceSTT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_ai = None
        self.gemini_cog = None
        self.listening = False
        self.temp_dir = "temp_stt"
        os.makedirs(self.temp_dir, exist_ok=True)

    async def ensure_cogs(self):
        if not self.voice_ai:
            self.voice_ai = self.bot.get_cog('VoiceAI')
        if not self.gemini_cog:
            self.gemini_cog = self.bot.get_cog('Gemini')

    # ====================== КОМАНДЫ ======================
    @commands.command(aliases=get_aliases("start_listen"))
    async def start_listen(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(get_message("voice_stt", "not_in_voice"))
        
        await self.ensure_cogs()
        if not self.voice_ai or not self.voice_ai.voice_client:
            return await ctx.send(get_message("voice_stt", "need_join_first"))

        self.listening = True
        await ctx.send(get_message("voice_stt", "listen_started"))

    @commands.command(aliases=get_aliases("stop_listen"))
    async def stop_listen(self, ctx):
        self.listening = False
        await ctx.send(get_message("voice_stt", "listen_stopped"))

    @commands.command(aliases=get_aliases("record_voice"))
    async def record_voice(self, ctx, duration: int = 6):
        """Записывает голос пользователя"""
        if not self.listening:
            return await ctx.send(get_message("voice_stt", "listen_not_enabled"))

        if not ctx.author.voice:
            return await ctx.send(get_message("voice_stt", "user_not_in_voice"))

        await self.ensure_cogs()
        vc = self.voice_ai.voice_client if self.voice_ai else None
        if not vc or not vc.is_connected():
            return await ctx.send(get_message("voice_stt", "bot_not_in_voice"))

        await ctx.send(get_message("voice_stt", "recording", duration=duration))

        filename = f"{self.temp_dir}/voice_{ctx.author.id}_{int(datetime.now().timestamp())}.wav"

        try:
            sink = voice_recv.WaveSink(destination=filename)

            vc.listen(sink)
            await asyncio.sleep(duration)
            vc.stop_listening()

            if os.path.exists(filename) and os.path.getsize(filename) > 1000:
                await ctx.send(get_message("voice_stt", "recording_success"))

                # TODO: Здесь позже подключишь Whisper
                transcribed = "тестовая запись голоса"   # заглушка

                if self.gemini_cog:
                    response = await self.gemini_cog.ask_gemini(ctx.channel.id, transcribed)
                else:
                    response = "Я не смогла обработать запись..."

                if (self.voice_ai and 
                    self.voice_ai.voice_client and 
                    self.voice_ai.voice_client.is_connected()):
                    await self.voice_ai.say(response)
                else:
                    await ctx.send(response)
            else:
                await ctx.send(get_message("voice_stt", "recording_empty"))

        except Exception as e:
            await ctx.send(get_message("voice_stt", "recording_error", error=str(e)))
            print(f"[VoiceSTT] Ошибка: {e}")
            import traceback
            traceback.print_exc()


async def setup(bot):
    await bot.add_cog(VoiceSTT(bot))
    print(get_message("voice_stt", "cog_loaded"))