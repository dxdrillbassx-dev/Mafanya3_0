# cogs/fun.py
import discord
from discord.ext import commands
import random

# Импорт алиасов
from utils.aliases import get_aliases


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=get_aliases("meme"))
    async def meme(self, ctx):
        """Пока заглушка для мемов"""
        await ctx.send("😔 Мемы пока в разработке... Скоро добавим!")

    @commands.command(aliases=get_aliases("eightball"))
    async def eightball(self, ctx, *, question: str = None):
        """Магический шар 8"""
        if not question:
            return await ctx.send("❓ Задай вопрос магическому шару!")
        
        responses = [
            "Да, определённо ✅",
            "Нет ❌",
            "Скорее всего да",
            "Не уверен...",
            "Можешь рассчитывать на это",
            "Лучше не стоит",
            "Даже не думай",
            "Конечно! 🔥",
            "Спроси позже",
            "Мой ответ — нет"
        ]
        await ctx.reply(f"🎱 **{random.choice(responses)}**")


async def setup(bot):
    await bot.add_cog(Fun(bot))