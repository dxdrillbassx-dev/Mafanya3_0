# utils/music_cover.py
import aiohttp
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import random
import textwrap
import os


class MusicCoverGenerator:
    def __init__(self):
        self.backgrounds_dir = "backgrounds"
        self.font_path = "Blackentina4F.ttf"  # должен лежать в корне проекта

    def get_random_background(self):
        """Выбирает случайный фон из папки backgrounds"""
        if not os.path.exists(self.backgrounds_dir):
            print(f"⚠️ Папка {self.backgrounds_dir} не найдена")
            return None
        
        valid = ('.jpg', '.jpeg', '.png', '.webp')
        images = [f for f in os.listdir(self.backgrounds_dir) if f.lower().endswith(valid)]
        
        if not images:
            print("⚠️ В папке backgrounds нет изображений")
            return None
            
        return os.path.join(self.backgrounds_dir, random.choice(images))

    async def create_cover(self, track_title: str, requester: str, avatar_url: str = None):
        """Создаёт красивую обложку для трека"""
        width, height = 1200, 675
        
        # Фон
        bg_path = self.get_random_background()
        if bg_path:
            try:
                img = Image.open(bg_path).convert("RGB").resize((width, height))
                blurred = img.filter(ImageFilter.GaussianBlur(radius=12))
                overlay = Image.new("RGB", (width, height), (0, 0, 0))
                img = Image.blend(blurred, overlay, alpha=0.65)
            except Exception as e:
                print(f"[Cover] Ошибка загрузки фона: {e}")
                img = Image.new("RGB", (width, height), (15, 15, 22))
        else:
            img = Image.new("RGB", (width, height), (15, 15, 22))

        draw = ImageDraw.Draw(img, "RGBA")

        # Загрузка шрифтов
        try:
            title_font = ImageFont.truetype(self.font_path, 78)
            name_font = ImageFont.truetype(self.font_path, 48)
            footer_font = ImageFont.truetype(self.font_path, 34)
        except:
            print("⚠️ Шрифт Blackentina4F.ttf не найден, используется стандартный")
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Основная рамка
        draw.rectangle([50, 50, width-50, height-90], 
                      fill=(0, 0, 0, 175), 
                      outline=(255, 105, 180), 
                      width=6)

        # Название трека
        title = track_title.replace('_', ' ').strip()
        if len(title) > 70:
            title = title[:67] + "..."
        
        wrapped = textwrap.fill(title, width=38)
        lines = wrapped.split('\n')
        
        y = 130
        for line in lines[:3]:
            font_size = 78 if len(line) <= 30 else 68 if len(line) <= 36 else 58
            try:
                current_font = ImageFont.truetype(self.font_path, font_size)
            except:
                current_font = title_font

            draw.text((100, y), line, fill=(255, 105, 180), font=current_font, 
                      stroke_width=6, stroke_fill=(0, 0, 0))
            y += font_size + 18

        # Аватарка + Ник
        avatar_y = y + 30
        avatar_size = 160

        if avatar_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(avatar_url) as resp:
                        avatar_data = await resp.read()
                
                avatar = Image.open(io.BytesIO(avatar_data)).convert("RGBA").resize((avatar_size, avatar_size))
                
                # Круглая аватарка
                mask = Image.new('L', (avatar_size, avatar_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
                avatar = ImageOps.fit(avatar, (avatar_size, avatar_size))
                avatar.putalpha(mask)
                
                # Розовая обводка
                border_size = avatar_size + 14
                border = Image.new('RGBA', (border_size, border_size), (255, 105, 180, 255))
                border_mask = Image.new('L', (border_size, border_size), 0)
                border_draw = ImageDraw.Draw(border_mask)
                border_draw.ellipse((0, 0, border_size, border_size), fill=255)
                border.putalpha(border_mask)
                
                paste_x = 100
                img.paste(border, (paste_x - 7, avatar_y - 7), border)
                img.paste(avatar, (paste_x, avatar_y), avatar)
            except Exception as e:
                print(f"[Cover] Ошибка аватарки: {e}")

        # Никнейм
        requester_text = f"Запросил: {requester}"
        draw.text((100 + avatar_size + 40, avatar_y + 50), requester_text, 
                  fill=(255, 200, 220), font=name_font, 
                  stroke_width=3, stroke_fill=(0, 0, 0))

        # Футер
        left_text = "Mafanya 3.0"
        right_text = "by Sobrina"
        
        draw.text((90, height-65), left_text, fill=(0, 0, 0), font=footer_font, stroke_width=4, stroke_fill=(0, 0, 0))
        draw.text((width - 255, height-65), right_text, fill=(0, 0, 0), font=footer_font, stroke_width=4, stroke_fill=(0, 0, 0))
        
        draw.text((85, height-65), left_text, fill=(200, 200, 220), font=footer_font)
        draw.text((width - 260, height-65), right_text, fill=(200, 200, 220), font=footer_font)

        # Сохранение
        filename = f"music_cover_{random.randint(100000, 999999)}.png"
        img.save(filename, quality=95)
        return filename