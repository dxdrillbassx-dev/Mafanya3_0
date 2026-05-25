# cogs/reload.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт

load_dotenv()

OWNER_ID = int(os.getenv('OWNER_ID', 0))


class ReloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, ctx):
        return ctx.author.id == OWNER_ID

    # ====================== RELOAD ======================
    @commands.command(aliases=get_aliases("reload"))
    async def reload(self, ctx, *extensions):
        """Перезагрузка модулей"""
        if not self.is_owner(ctx):
            return await ctx.send(get_message("reload", "access_denied"), delete_after=8)

        if not extensions:
            return await ctx.send(get_message("reload", "no_module_specified"))

        if extensions[0].lower() in ['all', 'все']:
            return await self.reload_all(ctx)

        for ext in extensions:
            await self._reload_single(ctx, ext)

    # ====================== RESTART ======================
    @commands.command(aliases=get_aliases("restart"))
    async def restart(self, ctx):
        """Полный перезапуск бота"""
        if not self.is_owner(ctx):
            return await ctx.send(get_message("reload", "access_denied"), delete_after=8)

        await ctx.send(get_message("reload", "restarting"))

        try:
            await self.bot.close()
        except Exception as e:
            await ctx.send(f"❌ Ошибка при попытке перезапуска:\n```{e}```")
            print(f"[ERROR] Restart failed: {e}")

    async def _reload_single(self, ctx, ext: str):
        """Перезагрузка одного модуля с защитой"""
        if not ext.startswith('cogs.'):
            full_ext = f"cogs.{ext}"
        else:
            full_ext = ext

        try:
            await self.bot.reload_extension(full_ext)
            await ctx.send(
                get_message("reload", "reload_success", module=ext), 
                delete_after=10
            )
            
        except commands.ExtensionNotLoaded:
            try:
                await self.bot.load_extension(full_ext)
                await ctx.send(
                    get_message("reload", "load_success", module=ext), 
                    delete_after=10
                )
            except Exception as e:
                await ctx.send(
                    get_message("reload", "load_error", module=ext), 
                    delete_after=15
                )
                
        except commands.CommandRegistrationError as e:
            await ctx.send(
                get_message("reload", "command_conflict", module=ext), 
                delete_after=20
            )
            
        except commands.ExtensionNotFound:
            await ctx.send(
                get_message("reload", "module_not_found", module=ext), 
                delete_after=10
            )
            
        except Exception as e:
            await ctx.send(
                get_message("reload", "reload_error", module=ext), 
                delete_after=15
            )

    # ====================== LOAD ======================
    @commands.command(aliases=get_aliases("load"))
    async def load(self, ctx, extension: str):
        """Загрузка модуля"""
        if not self.is_owner(ctx):
            return await ctx.send(get_message("reload", "access_denied"), delete_after=8)

        if not extension.startswith('cogs.'):
            extension = f"cogs.{extension}"

        try:
            await self.bot.load_extension(extension)
            await ctx.send(
                get_message("reload", "load_success", module=extension), 
                delete_after=10
            )
        except Exception as e:
            await ctx.send(f"❌ Ошибка загрузки:\n```{e}```", delete_after=15)

    # ====================== UNLOAD ======================
    @commands.command(aliases=get_aliases("unload"))
    async def unload(self, ctx, extension: str):
        """Выгрузка модуля"""
        if not self.is_owner(ctx):
            return await ctx.send(get_message("reload", "access_denied"), delete_after=8)

        if not extension.startswith('cogs.'):
            extension = f"cogs.{extension}"

        try:
            await self.bot.unload_extension(extension)
            await ctx.send(
                get_message("reload", "unload_success", module=extension), 
                delete_after=10
            )
        except commands.ExtensionNotLoaded:
            await ctx.send(
                get_message("reload", "module_not_loaded", module=extension)
            )
        except Exception as e:
            await ctx.send(
                get_message("reload", "unload_error"), 
                delete_after=15
            )

    # ====================== RELOAD ALL ======================
    @commands.command(aliases=get_aliases("reload_all"))
    async def reload_all(self, ctx):
        """Полная перезагрузка всех модулей"""
        if not self.is_owner(ctx):
            return await ctx.send(get_message("reload", "access_denied"))

        await ctx.send(get_message("reload", "reloading_all"))

        successful = []
        failed = []

        for root, dirs, files in os.walk('./cogs'):
            for filename in files:
                if filename.endswith('.py') and not filename.startswith('__'):
                    rel_path = os.path.relpath(os.path.join(root, filename), './cogs')
                    module_path = rel_path.replace(os.sep, '.')[:-3]
                    full_path = f"cogs.{module_path}"

                    try:
                        await self.bot.reload_extension(full_path)
                        successful.append(module_path)
                    except commands.ExtensionNotLoaded:
                        try:
                            await self.bot.load_extension(full_path)
                            successful.append(module_path)
                        except Exception as e:
                            failed.append(f"{module_path} → {type(e).__name__}")
                    except Exception as e:
                        failed.append(f"{module_path} → {type(e).__name__}")

        embed = discord.Embed(
            title=get_message("reload", "full_reload_title"), 
            color=0xFF69B4
        )
        embed.add_field(
            name=get_message("reload", "full_reload_success"), 
            value=f"`{len(successful)}`", 
            inline=True
        )
        
        if failed:
            embed.add_field(
                name=get_message("reload", "full_reload_errors"), 
                value=f"`{len(failed)}`", 
                inline=True
            )
            embed.description = "```" + "\n".join(failed[:10]) + "```"

        await ctx.send(embed=embed)


async def setup(bot):
    if OWNER_ID == 0:
        print(get_message("reload", "owner_id_missing"))
    await bot.add_cog(ReloadCog(bot))