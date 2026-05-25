# cogs/vkphoto.py
import discord
from discord.ext import commands
import random
import vk_api
import os

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт


class VKPhoto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vk = None
        self.setup_vk()

    def setup_vk(self):
        """Инициализация VK API"""
        try:
            token = os.getenv('VK_TOKEN')
            if not token:
                print(get_message("vkphoto", "token_missing"))
                return

            vk_session = vk_api.VkApi(token=token)
            self.vk = vk_session.get_api()
            
            me = self.vk.users.get(v="5.199")[0]
            print(get_message("vkphoto", "vk_connected", 
                            name=f"{me['first_name']} {me['last_name']}", 
                            id=me['id']))
            
        except Exception as e:
            print(get_message("vkphoto", "vk_connection_error", error=str(e)))

    def get_random_photo_url(self):
        """Получает случайное фото из сохранённых"""
        if not self.vk:
            return None

        try:
            # Основной запрос — Избранное
            response = self.vk.fave.getPhotos(count=50, photo_sizes=1, v="5.199")
            items = response.get('items', [])

            # Если мало фото — добавляем из альбома "Сохранённые"
            if len(items) < 10:
                try:
                    user = self.vk.users.get(v="5.199")[0]
                    response2 = self.vk.photos.get(
                        owner_id=user['id'],
                        album_id='saved',
                        count=50,
                        photo_sizes=1,
                        v="5.199"
                    )
                    items.extend(response2.get('items', []))
                except:
                    pass

            if not items:
                return None

            photo = random.choice(items)
            sizes = photo.get('sizes', [])

            if sizes:
                # Лучшее качество
                best = max(sizes, key=lambda x: x.get('width', 0) * x.get('height', 0))
                return best['url']

            # Fallback
            return (
                photo.get('photo_1280') or
                photo.get('photo_807') or
                photo.get('photo_604') or
                photo.get('photo_130')
            )

        except Exception as e:
            print(f"VK API Error: {e}")
            return None

    @commands.command(
        name="vkphoto",
        aliases=get_aliases("vkphoto")
    )
    async def vkphoto(self, ctx):
        """Случайная фотка из сохранённых в ВК"""
        if not self.vk:
            return await ctx.send(get_message("vkphoto", "api_not_connected"))

        async with ctx.typing():
            photo_url = self.get_random_photo_url()

        if not photo_url:
            return await ctx.send(get_message("vkphoto", "no_photo"))

        embed = discord.Embed(color=0xFF69B4)
        embed.set_image(url=photo_url)
        embed.set_footer(
            text=get_message("vkphoto", "embed_footer", author=ctx.author)
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(VKPhoto(bot))