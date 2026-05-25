# cogs/structure.py
import discord
from discord.ext import commands
from launcher.structure import get_project_structure

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт


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
            title=get_message("structure", "embed_title"),
            description=get_project_structure(),
            color=0xFF69B4
        )
        embed.set_footer(
            text=get_message("structure", "footer", author=ctx.author)
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ProjectStructure(bot))