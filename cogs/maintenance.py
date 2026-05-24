# cogs/maintenance.py
import discord
from discord.ext import commands
import os
import json

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
                await ctx.send("🚨 **ПОЛНЫЙ ТЕХРЕЖИМ** активен (выключается только через лаунчер)")
            elif maintenance_mode:
                await ctx.send("🟡 Техрежим включён (кроме владельца)")
            else:
                await ctx.send("🟢 Техрежим выключен")
            return

        arg = arg.lower()

        if arg in ['all', 'full', 'полный']:
            full_maintenance_mode = True
            maintenance_mode = False
            await ctx.send("🚨 **ПОЛНЫЙ ТЕХРЕЖИМ ВКЛЮЧЁН**\nТеперь **никто** не может использовать команды.")
            self.save_status(True)
            await self.send_log("🚨 Полный техрежим включён")

        elif arg in ['on', 'вкл', '1', 'enable']:
            full_maintenance_mode = False
            maintenance_mode = True
            await ctx.send("🟡 **Техрежим включён** (все кроме тебя)")
            self.save_status(False)
            await self.send_log("🟡 Обычный техрежим включён")

        elif arg in ['off', 'выкл', '0', 'disable']:
            if full_maintenance_mode:
                await ctx.send("❌ Полный техрежим можно выключить **только через лаунчер**.")
            else:
                maintenance_mode = False
                await ctx.send("🟢 Техрежим выключен")
                self.save_status(False)
                await self.send_log("🟢 Техрежим выключен")
        else:
            await ctx.send("`!tech` — статус\n`!tech on` — кроме owner\n`!tech all` — полный")

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
    print("✅ Maintenance cog загружен с partial/full режимом")