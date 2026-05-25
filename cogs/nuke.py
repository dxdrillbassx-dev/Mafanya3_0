import discord
from discord.ext import commands
import os
import sys
import asyncio
import time

class Nuke(commands.Cog):
    """Cog для полного уничтожения бота"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nuke", aliases=["selfdestruct", "destroy", "полныйснос", "killall"])
    @commands.is_owner()
    async def nuke_bot(self, ctx):
        """Полное уничтожение бота (только для владельца)"""
        
        embed = discord.Embed(
            title="☢ ИНИЦИИРУЮ ПОЛНЫЙ СНОС",
            description="**Mafanya 3.0** будет полностью уничтожена через 3 секунды...",
            color=0xFF0000
        )
        embed.set_footer(text="Self-Destruct Protocol • Только Owner")
        await ctx.send(embed=embed)

        # Выходим из всех голосовых каналов
        for vc in self.bot.voice_clients:
            try:
                await vc.disconnect(force=True)
            except:
                pass

        await asyncio.sleep(1.5)

        # Финальное сообщение
        final_embed = discord.Embed(
            title="💥 БОТ УНИЧТОЖЕН",
            description="Процесс завершён.\nMafanya 3.0 больше не в сети.",
            color=0x8B0000
        )
        try:
            await ctx.send(embed=final_embed)
        except:
            pass

        print("\n" + "="*60)
        print("☢ КОМАНДА !NUKE ВЫПОЛНЕНА — ПОЛНОЕ УНИЧТОЖЕНИЕ БОТА")
        print("="*60)

        # Даём время на отправку сообщений
        await asyncio.sleep(2)

        # === ЖЁСТКОЕ ЗАВЕРШЕНИЕ ===
        try:
            await self.bot.close()
        except:
            pass

        # Самые надёжные способы убийства процесса
        try:
            os._exit(0)
        except:
            pass
        
        try:
            sys.exit(0)
        except:
            pass

        # Если ничего не помогло
        import signal
        os.kill(os.getpid(), signal.SIGTERM)


    @commands.command(name="nukestatus")
    @commands.is_owner()
    async def nuke_status(self, ctx):
        """Проверка, работает ли nuke cog"""
        await ctx.send("✅ **Nuke Module активен.** Команда `!nuke` готова к использованию.")


async def setup(bot):
    await bot.add_cog(Nuke(bot))
    print("☢ Nuke Cog успешно загружен | Команда: !nuke")