# cogs/audio.py
import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque
import datetime
import os
import sys

# Импорт алиасов
from utils.aliases import get_aliases

# Исправленный импорт
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.music_cover import MusicCoverGenerator


class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.last_channel = {}
        self.cover_generator = MusicCoverGenerator()

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    def create_embed(self, track, queue_len=0, status="▶️ Сейчас играет"):
        embed = discord.Embed(title=status, description=f"**{track['title'][:80]}**", color=0xFF69B4)
        embed.add_field(name="Запросил", value=track.get('requester_mention', '—'), inline=True)
        
        if track.get('duration'):
            m, s = divmod(int(track.get('duration', 0)), 60)
            embed.add_field(name="Длительность", value=f"`{m:02d}:{s:02d}`", inline=True)
        if queue_len > 0:
            embed.add_field(name="В очереди", value=str(queue_len), inline=True)

        now = datetime.datetime.now()
        embed.set_footer(text=f"Запросил: {track['requester']} • {now.strftime('%H:%M')}")
        embed.timestamp = now
        return embed

    @commands.command(aliases=get_aliases("play"))
    async def play(self, ctx, *, url: str = None):
        try: 
            await ctx.message.delete()
        except: 
            pass
        
        if not url:
            return await ctx.send("❌ Укажи ссылку!", delete_after=12)
        if not ctx.author.voice:
            return await ctx.send("❌ Зайди в голосовой канал!", delete_after=10)

        await self.ensure_voice(ctx)
        msg = await ctx.send("🔍 **Ищу трек...**")

        try:
            with yt_dlp.YoutubeDL({
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }) as ydl:
                info = ydl.extract_info(url, download=False)

            track = {
                'audio_url': info['url'],
                'title': info.get('title', url),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'requester': str(ctx.author),
                'requester_mention': ctx.author.mention,
                'is_file': False
            }

            queue = self.get_queue(ctx.guild.id)
            queue.append(track)
            await msg.delete()

            if not ctx.voice_client.is_playing():
                await self.play_next(ctx.guild, ctx.channel)
            else:
                await ctx.send(f"✅ Добавлено: **{track['title'][:60]}**", delete_after=12)

        except Exception as e:
            await msg.delete()
            await ctx.send(f"❌ Ошибка: {str(e)[:150]}", delete_after=15)

    async def ensure_voice(self, ctx_or_msg):
        vc = ctx_or_msg.guild.voice_client
        if not vc:
            await ctx_or_msg.author.voice.channel.connect()
        elif vc.channel != ctx_or_msg.author.voice.channel:
            await vc.move_to(ctx_or_msg.author.voice.channel)

    async def play_next(self, guild, text_channel=None):
        queue = self.get_queue(guild.id)
        if not queue:
            await asyncio.sleep(20)
            if guild.voice_client and len(guild.voice_client.channel.members) <= 1:
                await guild.voice_client.disconnect()
                self.queues.pop(guild.id, None)
            return

        track = queue.popleft()
        voice_client = guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return

        if text_channel:
            self.last_channel[guild.id] = text_channel

        try:
            embed = self.create_embed(track, len(queue))
            if track.get('thumbnail'):
                embed.set_image(url=track['thumbnail'])
            
            channel = self.last_channel.get(guild.id) or text_channel
            await channel.send(embed=embed)

            source = discord.FFmpegPCMAudio(
                track['audio_url'],
                before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5' if not track.get('is_file') else None,
                options='-vn -ac 2 -ar 48000'
            )

            def after(error):
                if error:
                    print(f"[FFmpeg] Ошибка: {error}")
                if track.get('temp_file') and os.path.exists(track['temp_file']):
                    try:
                        os.remove(track['temp_file'])
                    except:
                        pass
                asyncio.run_coroutine_threadsafe(self.play_next(guild), self.bot.loop)

            voice_client.play(source, after=after)
            print(f"▶️ Играет: {track['title'][:70]}")

        except Exception as e:
            print(f"[play_next] Критическая ошибка: {e}")
            if track.get('temp_file') and os.path.exists(track['temp_file']):
                try: os.remove(track['temp_file'])
                except: pass
            await asyncio.sleep(2)
            await self.play_next(guild)

    # ==================== Управление ====================
    @commands.command(aliases=get_aliases("skip"))
    async def skip(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            ctx.voice_client.stop()
            await ctx.send("⏭ **Пропущено**", delete_after=8)

    @commands.command(aliases=get_aliases("pause"))
    async def pause(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸ **Пауза**", delete_after=10)

    @commands.command(aliases=get_aliases("resume"))
    async def resume(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ **Продолжаю**", delete_after=10)

    @commands.command(aliases=get_aliases("leave"))
    async def leave(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queues.pop(ctx.guild.id, None)
            await ctx.send("👋 **Отключился**", delete_after=8)


async def setup(bot):
    await bot.add_cog(Audio(bot))