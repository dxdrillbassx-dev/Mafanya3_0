# cogs/audio_files.py
import discord
from discord.ext import commands
import asyncio
import os

from utils.aliases import get_aliases
from utils.module_descriptions import get_message


class AudioFiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
                return  # только один файл за сообщение

    async def play_audio_file(self, message: discord.Message, attachment):
        try:
            if not message.author.voice:
                return await message.channel.send(
                    get_message("audio_files", "not_in_voice", "Ты должен быть в голосовом канале"), 
                    delete_after=10
                )

            await self.ensure_voice(message)

            # Сохраняем файл
            file_path = os.path.join(self.temp_dir, attachment.filename)
            await attachment.save(file_path)

            track = {
                'audio_url': file_path,
                'title': attachment.filename.replace('_', ' ').replace('.mp3', '').replace('.wav', ''),
                'requester': str(message.author),
                'requester_mention': message.author.mention,
                'is_file': True,
                'temp_file': file_path
            }

            audio_cog = self.bot.get_cog('Audio')
            if not audio_cog:
                return await message.channel.send("❌ Музыкальный модуль не загружен.")

            queue = audio_cog.get_queue(message.guild.id)
            queue.append(track)

            if not message.guild.voice_client.is_playing():
                await audio_cog.play_next(message.guild, message.channel)
            else:
                await message.channel.send(
                    get_message("audio_files", "file_added", "✅ Файл добавлен: **{title}**", title=track['title'][:60]),
                    delete_after=12
                )

        except Exception as e:
            await message.channel.send(
                get_message("audio_files", "play_error", "❌ Ошибка при воспроизведении файла: {error}", error=str(e)[:100]),
                delete_after=15
            )

    async def ensure_voice(self, msg):
        vc = msg.guild.voice_client
        if not vc:
            await msg.author.voice.channel.connect()
        elif vc.channel != msg.author.voice.channel:
            await vc.move_to(msg.author.voice.channel)


async def setup(bot):
    await bot.add_cog(AudioFiles(bot))