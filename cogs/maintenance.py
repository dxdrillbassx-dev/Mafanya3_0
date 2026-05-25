# cogs/maintenance.py
import discord
from discord.ext import commands
import os
import json

from utils.module_descriptions import get_message   # ← Главный импорт

# Глобальные переменные
maintenance_mode = False      # Обычный режим (кроме owner)
full_maintenance_mode = False # Полный режим (даже owner)


class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['тех', 'обслуживание', 'maintenance', 'техрежим'])
    @commands.check(lambda ctx: ctx.author.id == ctx.bot.owner_id)
    async def tech(self, ctx, arg: str = None):
        global maintenance_mode, full_maintenance_mode

        if arg is None:
            if full_maintenance_mode:
                await ctx.send(get_message("maintenance", "full_active"))
            elif maintenance_mode:
                await ctx.send(get_message("maintenance", "partial_active"))
            else:
                await ctx.send(get_message("maintenance", "disabled"))
            return

        arg = arg.lower()

        if arg in ['all', 'full', 'полный']:
            full_maintenance_mode = True
            maintenance_mode = False
            await ctx.send(get_message("maintenance", "full_enabled"))
            self.save_status(True)
            await self.send_log(get_message("maintenance", "log_full"))

        elif arg in ['on', 'вкл', '1', 'enable']:
            full_maintenance_mode = False
            maintenance_mode = True
            await ctx.send(get_message("maintenance", "partial_enabled"))
            self.save_status(False)
            await self.send_log(get_message("maintenance", "log_partial"))

        elif arg in ['off', 'выкл', '0', 'disable']:
            if full_maintenance_mode:
                await ctx.send(get_message("maintenance", "full_cannot_disable"))
            else:
                maintenance_mode = False
                await ctx.send(get_message("maintenance", "disabled_success"))
                self.save_status(False)
                await self.send_log(get_message("maintenance", "log_disabled"))
        else:
            await ctx.send(get_message("maintenance", "help"))

    def save_status(self, full: bool):
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/maintenance_status.json", "w", encoding="utf-8") as f:
                json.dump({"full_maintenance": full}, f)
        except:
            pass

    async def send_log(self, message: str):
        if hasattr(self.bot, 'send_log'):
            await self.bot.send_log(message)


# Проверка перед каждой командой
def check_maintenance(ctx):
    if full_maintenance_mode:
        return False  # Никто не может
    if maintenance_mode:
        return ctx.author.id == getattr(ctx.bot, 'owner_id', 0)
    return True


async def setup(bot):
    await bot.add_cog(Maintenance(bot))
    bot.owner_id = int(os.getenv('OWNER_ID', 0))
    bot.check(check_maintenance)   # Глобальная проверка
    print(get_message("maintenance", "cog_loaded"))