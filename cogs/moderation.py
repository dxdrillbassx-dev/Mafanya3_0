# cogs/moderation.py
import discord
from discord.ext import commands

# Импорт алиасов
from utils.aliases import get_aliases


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==================== БАН ====================
    @commands.command(aliases=get_aliases("ban"))
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Без причины"):
        """Забанить участника"""
        if member == ctx.author:
            return await ctx.send("❌ Нельзя забанить самого себя!")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ У тебя недостаточно прав для бана этого участника.")

        try:
            await member.ban(reason=reason)
            await ctx.send(f"✅ **{member}** был забанен.\nПричина: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Не удалось забанить: {e}")

    # ==================== КИК ====================
    @commands.command(aliases=get_aliases("kick"))
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Без причины"):
        """Выгнать участника"""
        if member == ctx.author:
            return await ctx.send("❌ Нельзя кикнуть самого себя!")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ У тебя недостаточно прав для кика этого участника.")

        try:
            await member.kick(reason=reason)
            await ctx.send(f"✅ **{member}** был кикнут.\nПричина: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Не удалось кикнуть: {e}")

    # ==================== МУТ (таймаут) ====================
    @commands.command(aliases=get_aliases("mute"))
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int = 10, *, reason: str = "Без причины"):
        """Выдать таймаут (мут) на указанное время"""
        if member == ctx.author:
            return await ctx.send("❌ Нельзя замутить самого себя!")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ У тебя недостаточно прав.")

        try:
            delta = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
            await member.timeout(delta, reason=reason)
            await ctx.send(f"🔇 **{member}** получил таймаут на **{minutes}** минут.\nПричина: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Не удалось выдать мут: {e}")

    # ==================== РАЗМУТ ====================
    @commands.command(aliases=get_aliases("unmute"))
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """Снять таймаут"""
        try:
            await member.timeout(None)
            await ctx.send(f"✅ С {member.mention} снят таймаут.")
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {e}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))