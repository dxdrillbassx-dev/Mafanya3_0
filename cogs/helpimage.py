# cogs/helpimage.py
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import random

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт


class HelpImageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backgrounds_dir = "backgrounds"
        self.font_path = "Blackentina4F.ttf"

    def get_random_background(self):
        if not os.path.exists(self.backgrounds_dir):
            return None
        valid = ('.jpg', '.jpeg', '.png', '.webp')
        images = [f for f in os.listdir(self.backgrounds_dir) if f.lower().endswith(valid)]
        return os.path.join(self.backgrounds_dir, random.choice(images)) if images else None

    def create_section_image(self, title: str, cmds: list):
        width, height = 1200, 720
        bg_path = self.get_random_background()

        if bg_path:
            try:
                img = Image.open(bg_path).convert("RGB").resize((width, height))
                blurred = img.filter(ImageFilter.GaussianBlur(radius=8))
                overlay = Image.new("RGB", (width, height), (0, 0, 0))
                img = Image.blend(blurred, overlay, alpha=0.65)
            except:
                img = Image.new("RGB", (width, height), (15, 15, 22))
        else:
            img = Image.new("RGB", (width, height), (15, 15, 22))

        draw = ImageDraw.Draw(img, "RGBA")

        try:
            title_font = ImageFont.truetype(self.font_path, 68)
            text_font = ImageFont.truetype(self.font_path, 32)
            footer_font = ImageFont.truetype(self.font_path, 27)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Центральная полупрозрачная карточка
        draw.rectangle([60, 60, width-60, height-100], 
                      fill=(0, 0, 0, 160), outline=(255, 105, 180), width=5)

        # Заголовок
        draw.text((100, 90), title, fill=(255, 105, 180), font=title_font, 
                 stroke_width=4, stroke_fill=(0, 0, 0))

        # Команды
        y = 190
        for cmd in cmds:
            draw.text((110, y+3), cmd, fill=(0, 0, 0), font=text_font, 
                     stroke_width=3, stroke_fill=(0, 0, 0))
            draw.text((105, y), cmd, fill=(230, 235, 255), font=text_font)
            y += 58

        # Нижний текст
        left_text = get_message("helpimage", "footer_left")
        right_text = get_message("helpimage", "footer_right")
        
        draw.text((90, height-68), left_text, fill=(0, 0, 0), font=footer_font, 
                 stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((width - 290, height-68), right_text, fill=(0, 0, 0), font=footer_font, 
                 stroke_width=4, stroke_fill=(0, 0, 0))
        
        draw.text((85, height-68), left_text, fill=(200, 200, 220), font=footer_font)
        draw.text((width - 295, height-68), right_text, fill=(200, 200, 220), font=footer_font)

        filename = f"mafanya_{title.split()[0].lower()}_{random.randint(1000,9999)}.png"
        img = img.convert("RGB")
        img.save(filename, quality=95)
        return filename

    @commands.command(aliases=get_aliases("helpimage"))
    async def helpimage(self, ctx):
        sections = [
            {
                "title": get_message("helpimage", "music_section"),
                "cmds": get_message("helpimage", "music_cmds")
            },
            {
                "title": get_message("helpimage", "roles_section"),
                "cmds": get_message("helpimage", "roles_cmds")
            },
            {
                "title": get_message("helpimage", "ai_section"),
                "cmds": get_message("helpimage", "ai_cmds")
            },
            {
                "title": get_message("helpimage", "pinterest_section"),
                "cmds": get_message("helpimage", "pinterest_cmds")
            },
        ]

        files = []
        filenames = []

        for sec in sections:
            filename = self.create_section_image(sec["title"], sec["cmds"])
            files.append(discord.File(filename))
            filenames.append(filename)

        embed = discord.Embed(
            title=get_message("helpimage", "menu_title"), 
            color=0xFF69B4
        )
        await ctx.send(embed=embed, files=files)

        # Удаляем временные файлы
        for fn in filenames:
            if os.path.exists(fn):
                try:
                    os.remove(fn)
                except:
                    pass


async def setup(bot):
    await bot.add_cog(HelpImageCog(bot))