# cogs/structure.py
import discord
from discord.ext import commands
from launcher.structure import get_project_structure

# Импорт алиасов
from utils.aliases import get_aliases


class ProjectStructure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=get_aliases("structure"))
    async def structure(self, ctx):
        """Показывает структуру проекта"""
        try:
            await ctx.message.delete()
        except:
            pass

        embed = discord.Embed(
            title="📁 Структура проекта Mafanya 3.0",
            description=get_project_structure(),
            color=0xFF69B4
        )
        embed.set_footer(text=f"Запросил: {ctx.author}")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ProjectStructure(bot))