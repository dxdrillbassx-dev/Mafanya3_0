# cogs/fun.py
import discord
from discord.ext import commands
import random

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=get_aliases("meme"))
    async def meme(self, ctx):
        """Пока заглушка для мемов"""
        await ctx.send(get_message("fun", "meme_placeholder"))

    @commands.command(aliases=get_aliases("eightball"))
    async def eightball(self, ctx, *, question: str = None):
        """Магический шар 8"""
        if not question:
            return await ctx.send(get_message("fun", "eightball_no_question"))
        
        responses = get_message("fun", "eightball_responses")
        response = random.choice(responses)
        
        await ctx.reply(get_message("fun", "eightball_answer", response=response))


async def setup(bot):
    await bot.add_cog(Fun(bot))