# cogs/customrole.py
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
import json
import os
import re
from datetime import datetime

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт для сообщений

DATA_FILE = "data/custom_roles.json"


def load_roles():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_roles(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ====================== МОДАЛКА СОЗДАНИЯ ======================
class CustomRoleModal(Modal, title=get_message("customrole", "create_modal_title")):
    def __init__(self):
        super().__init__(timeout=None)
        self.role_name = TextInput(
            label=get_message("customrole", "create_name_label"),
            placeholder="Не ITшник",
            required=True,
            max_length=80
        )
        self.icon_url = TextInput(
            label=get_message("customrole", "create_icon_label"),
            placeholder="https://...",
            required=False
        )
        self.color = TextInput(
            label=get_message("customrole", "create_color_label"),
            placeholder="#FF69B4",
            required=True,
            max_length=7
        )
        self.hoist = TextInput(
            label=get_message("customrole", "create_hoist_label"),
            placeholder="да",
            required=True,
            max_length=3
        )
        
        self.add_item(self.role_name)
        self.add_item(self.icon_url)
        self.add_item(self.color)
        self.add_item(self.hoist)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        color_hex = self.color.value.strip()
        if not re.match(r'^#?[0-9a-fA-F]{6}$', color_hex):
            return await interaction.followup.send(
                get_message("customrole", "invalid_hex"), 
                ephemeral=True
            )
        
        color = discord.Color(int(color_hex.strip('#'), 16))
        hoist = self.hoist.value.lower() in ['да', 'yes', '1', 'true']
        
        try:
            role = await interaction.guild.create_role(
                name=self.role_name.value.strip(),
                color=color,
                hoist=hoist,
                reason=f"Личная роль | {interaction.user}"
            )
            await interaction.user.add_roles(role)

            data = load_roles()
            data[str(role.id)] = {
                "name": role.name,
                "owner": interaction.user.id,
                "owner_name": str(interaction.user),
                "color": color_hex,
                "created_at": datetime.now().isoformat()
            }
            save_roles(data)

            embed = discord.Embed(
                title=get_message("customrole", "role_created_title"), 
                color=color
            )
            embed.add_field(
                name=get_message("customrole", "role_created_field"),
                value=role.mention
            )
            await interaction.followup.send(embed=embed, ephemeral=False)
        except Exception as e:
            await interaction.followup.send(
                get_message("errors", "bot_error", text=str(e)), 
                ephemeral=True
            )


# ====================== МОДАЛКА УДАЛЕНИЯ ======================
class DeleteRoleModal(Modal, title=get_message("customrole", "delete_modal_title")):
    def __init__(self):
        super().__init__(timeout=None)
        self.role_id = TextInput(
            label=get_message("customrole", "delete_id_label"),
            placeholder="Вставь ID роли сюда",
            required=True,
            max_length=20
        )
        self.reason = TextInput(
            label=get_message("customrole", "delete_reason_label"),
            placeholder="Не нужна / нарушение / и т.д.",
            required=False,
            style=discord.TextStyle.short
        )
        self.add_item(self.role_id)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            role_id = int(self.role_id.value.strip())
            role = interaction.guild.get_role(role_id)
            
            if not role:
                return await interaction.followup.send(
                    get_message("customrole", "role_not_found"), 
                    ephemeral=True
                )
            
            role_name = role.name
            await role.delete(reason=self.reason.value or f"Удалено админом {interaction.user}")
            
            data = load_roles()
            if str(role_id) in data:
                del data[str(role_id)]
                save_roles(data)
            
            await interaction.followup.send(
                get_message("customrole", "role_deleted", role_name=role_name), 
                ephemeral=False
            )
            
        except ValueError:
            await interaction.followup.send(
                get_message("customrole", "invalid_id"), 
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                get_message("errors", "bot_error", text=str(e)), 
                ephemeral=True
            )


# ====================== COG ======================
class CustomRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=get_aliases("createrole"))
    async def createrole(self, ctx):
        """Создать личную роль"""
        embed = discord.Embed(
            title=get_message("customrole", "createrole_title"),
            description=get_message("customrole", "createrole_description"),
            color=0xFF69B4
        )
        view = View(timeout=None)
        btn = Button(label="Создать роль", style=discord.ButtonStyle.primary, emoji="✨")
        btn.callback = lambda i: i.response.send_modal(CustomRoleModal())
        view.add_item(btn)
        await ctx.send(embed=embed, view=view)
        try: 
            await ctx.message.delete()
        except: 
            pass

    @commands.command(aliases=get_aliases("listcustomroles"))
    @commands.has_permissions(administrator=True)
    async def listcustomroles(self, ctx):
        """Список личных ролей + удаление"""
        data = load_roles()
        if not data:
            return await ctx.send(get_message("customrole", "listroles_no_roles"))

        embed = discord.Embed(
            title=get_message("customrole", "listroles_title"), 
            color=0xFF0000
        )
        embed.description = get_message("customrole", "listroles_description")
        
        for role_id, info in data.items():
            embed.description += f"`{role_id}` → **{info['name']}** (владелец: <@{info['owner']}>\n"
        
        view = View(timeout=None)
        btn = Button(label="Удалить роль", style=discord.ButtonStyle.red, emoji="🗑️")
        btn.callback = lambda i: i.response.send_modal(DeleteRoleModal())
        view.add_item(btn)

        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(CustomRoleCog(bot))