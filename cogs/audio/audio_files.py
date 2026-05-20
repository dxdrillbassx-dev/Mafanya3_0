# cogs/audio_files.py
import discord
from discord.ext import commands
import asyncio
import os
import sys

# Импорт алиасов (для единообразия)
from utils.aliases import get_aliases

# Исправленный импорт
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.music_cover import MusicCoverGenerator


class AudioFiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cover_generator = MusicCoverGenerator()
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return

        for att in message.attachments:
            if att.filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac')):
                await self.play_audio_file(message, att)
                try:
                    await message.delete()
                except:
                    pass
                return  # Обрабатываем только один файл за раз

    async def play_audio_file(self, message: discord.Message, attachment):
        try:
            if not message.author.voice:
                return await message.channel.send("❌ Зайди в голосовой канал!", delete_after=10)

            await self.ensure_voice(message)

            # Сохраняем файл
            file_path = os.path.join(self.temp_dir, attachment.filename)
            await attachment.save(file_path)

            track = {
                'audio_url': file_path,
                'title': attachment.filename.replace('_', ' '),
                'requester': str(message.author),
                'requester_mention': message.author.mention,
                'is_file': True,
                'temp_file': file_path
            }

            audio_cog = self.bot.get_cog('Audio')
            if not audio_cog:
                return await message.channel.send("❌ Основной модуль музыки не загружен.")

            queue = audio_cog.get_queue(message.guild.id)
            queue.append(track)

            if not message.guild.voice_client.is_playing():
                await audio_cog.play_next(message.guild, message.channel)
            else:
                await message.channel.send(f"✅ Добавлен файл: **{track['title'][:60]}**", delete_after=12)

        except Exception as e:
            await message.channel.send(f"❌ Ошибка при воспроизведении файла: {str(e)[:100]}", delete_after=15)

    async def ensure_voice(self, ctx_or_msg):
        vc = ctx_or_msg.guild.voice_client
        if not vc:
            await ctx_or_msg.author.voice.channel.connect()
        elif vc.channel != ctx_or_msg.author.voice.channel:
            await vc.move_to(ctx_or_msg.author.voice.channel)


async def setup(bot):
    await bot.add_cog(AudioFiles(bot))