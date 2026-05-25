# cogs/moderation.py
import discord
from discord.ext import commands

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==================== БАН ====================
    @commands.command(aliases=get_aliases("ban"))
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Без причины"):
        """Забанить участника"""
        if member == ctx.author:
            return await ctx.send(get_message("moderation", "ban_self"))
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(get_message("moderation", "ban_no_perms"))

        try:
            await member.ban(reason=reason)
            await ctx.send(get_message("moderation", "ban_success", 
                                     member=member, reason=reason))
        except Exception as e:
            await ctx.send(get_message("moderation", "ban_error", error=str(e)))

    # ==================== КИК ====================
    @commands.command(aliases=get_aliases("kick"))
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Без причины"):
        """Выгнать участника"""
        if member == ctx.author:
            return await ctx.send(get_message("moderation", "kick_self"))
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(get_message("moderation", "kick_no_perms"))

        try:
            await member.kick(reason=reason)
            await ctx.send(get_message("moderation", "kick_success", 
                                     member=member, reason=reason))
        except Exception as e:
            await ctx.send(get_message("moderation", "kick_error", error=str(e)))

    # ==================== МУТ (таймаут) ====================
    @commands.command(aliases=get_aliases("mute"))
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int = 10, *, reason: str = "Без причины"):
        """Выдать таймаут (мут) на указанное время"""
        if member == ctx.author:
            return await ctx.send(get_message("moderation", "mute_self"))
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(get_message("moderation", "mute_no_perms"))

        try:
            delta = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
            await member.timeout(delta, reason=reason)
            await ctx.send(get_message("moderation", "mute_success", 
                                     member=member, minutes=minutes, reason=reason))
        except Exception as e:
            await ctx.send(get_message("moderation", "mute_error", error=str(e)))

    # ==================== РАЗМУТ ====================
    @commands.command(aliases=get_aliases("unmute"))
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """Снять таймаут"""
        try:
            await member.timeout(None)
            await ctx.send(get_message("moderation", "unmute_success", member=member.mention))
        except Exception as e:
            await ctx.send(get_message("moderation", "unmute_error", error=str(e)))


async def setup(bot):
    await bot.add_cog(Moderation(bot))