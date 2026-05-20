# cogs/pinterest.py
import discord
from discord.ext import commands
import random
import json
import os
from py3pin.Pinterest import Pinterest
from dotenv import load_dotenv
from datetime import datetime

# Импорт алиасов
from utils.aliases import get_aliases

load_dotenv()


class PinterestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_username = "askerka110038302"
        
        self.history_file = "data/pinterest_history.json"
        self.history = self.load_history()

        self.pinterest_client = Pinterest(
            email=os.getenv("PINTEREST_EMAIL"),
            password=os.getenv("PINTEREST_PASSWORD"),
            username=self.default_username,
            cred_root="pinterest_cred"
        )

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_history(self):
        os.makedirs("data", exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add_to_history(self, username: str, pin_id: str):
        if username not in self.history:
            self.history[username] = []
        if pin_id not in self.history[username]:
            self.history[username].append(pin_id)
        
        if len(self.history[username]) > 2000:
            self.history[username] = self.history[username][-2000:]
        self.save_history()

    @commands.command(aliases=get_aliases("pinterest"))
    async def pinterest(self, ctx, target_username: str = None):
        """Прямая команда — с удалением сообщения и показом 'Ищу...'"""
        try:
            await ctx.message.delete()
        except:
            pass

        await self.send_random_pin(ctx, target_username, show_search_message=True)

    async def send_random_pin(self, ctx, target_username: str = None, show_search_message: bool = False):
        """Основная логика отправки пина"""
        username = target_username.lstrip('@') if target_username else self.default_username

        search_msg = None
        if show_search_message:
            search_msg = await ctx.send(f"🔍 Ищу новые пины **@{username}**...")

        try:
            pins = self.pinterest_client.get_user_pins(
                username=username, 
                reset_bookmark=True
            )

            if not pins:
                if search_msg:
                    await search_msg.edit(content=f"❌ Пины пользователя **@{username}** не найдены.")
                else:
                    await ctx.send(f"❌ Пины пользователя **@{username}** не найдены.")
                return

            used = self.history.get(username, [])
            available = [p for p in pins if str(p.get('id')) not in used]

            if len(available) < 10:
                self.history[username] = used[-800:]
                available = [p for p in pins if str(p.get('id')) not in self.history.get(username, [])]

            if not available:
                if search_msg:
                    await search_msg.edit(content="❌ Все доступные пины уже были показаны.")
                else:
                    await ctx.send("❌ Все доступные пины уже были показаны.")
                return

            pin = random.choice(available)
            pin_id = str(pin.get('id'))
            
            image_url = (pin.get('images', {})
                           .get('orig', {})
                           .get('url') or 
                         pin.get('image_large_url') or 
                         pin.get('image_medium_url'))

            if search_msg:
                try:
                    await search_msg.delete()
                except:
                    pass

            # Отправляем сам пин
            now = datetime.now()
            time_str = now.strftime("%H:%M")
            requester = ctx.author.display_name or ctx.author.name

            embed = discord.Embed(
                title="📌 Pinterest", 
                color=0xFF69B4,
                url=f"https://www.pinterest.com/{username}/"
            )
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Запросил: {requester} • Сегодня, в {time_str}")

            await ctx.send(embed=embed)
            self.add_to_history(username, pin_id)

        except Exception as e:
            print(f"Pinterest error for @{username}: {e}")
            error_text = "❌ Ошибка при получении пинов."
            if search_msg:
                try:
                    await search_msg.edit(content=error_text)
                except:
                    await ctx.send(error_text)
            else:
                await ctx.send(error_text)


async def setup(bot):
    await bot.add_cog(PinterestCog(bot))