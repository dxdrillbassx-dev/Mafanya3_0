# cogs/basic.py
import discord
import datetime
from discord.ext import commands
from utils.aliases import get_aliases
from utils.module_descriptions import get_message  # ← главный импорт


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=get_aliases("ping"))
    async def ping(self, ctx):
        """Пинг бота"""
        latency = round(self.bot.latency * 1000)
        await ctx.reply(get_message("basic", "ping", latency=latency))

    @commands.command(aliases=get_aliases("hello"))
    async def hello(self, ctx):
        """Приветствие"""
        await ctx.reply(get_message("basic", "hello", member=ctx.author.mention))

    @commands.command(aliases=get_aliases("about"))
    async def about(self, ctx):
        """Информация о боте"""
        embed = discord.Embed(
            title=get_message("basic", "about_title"),
            description=get_message("basic", "about_description"),
            color=0xFF69B4
        )
        embed.add_field(
            name=get_message("basic", "about_prefix"),
            value=get_message("basic", "about_prefix_value"),
            inline=True
        )
        embed.add_field(
            name=get_message("basic", "about_commands"),
            value=get_message("basic", "about_commands_value"),
            inline=True
        )
        embed.set_footer(text=get_message("basic", "about_footer"))
        await ctx.reply(embed=embed)

    @commands.command(aliases=get_aliases("clear"))
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """Очистка сообщений"""
        if amount < 1:
            amount = 1
        if amount > 100:
            amount = 100
            
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(
            get_message("basic", "clear_success", amount=amount), 
            delete_after=5
        )

    @commands.command(aliases=get_aliases("userinfo"))
    async def userinfo(self, ctx, member: discord.Member = None):
        """Показывает ID пользователя"""
        member = member or ctx.author

        embed = discord.Embed(
            title=get_message("basic", "userinfo_title"),
            color=0xFF69B4
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(
            name=get_message("basic", "userinfo_name"),
            value=f"{member} (`{member.display_name}`)",
            inline=False
        )
        embed.add_field(
            name=get_message("basic", "userinfo_id"),
            value=f"`{member.id}`",
            inline=False
        )
        embed.add_field(
            name=get_message("basic", "userinfo_mention"),
            value=member.mention,
            inline=False
        )
        embed.add_field(
            name=get_message("basic", "userinfo_created"),
            value=member.created_at.strftime("%d.%m.%Y"),
            inline=True
        )
        embed.add_field(
            name=get_message("basic", "userinfo_joined"),
            value=member.joined_at.strftime("%d.%m.%Y") if member.joined_at else "Неизвестно",
            inline=True
        )
        
        await ctx.reply(embed=embed)

    @commands.command(aliases=get_aliases("myid"))
    async def myid(self, ctx):
        """Показывает только твой ID"""
        await ctx.reply(get_message("basic", "myid", id=ctx.author.id))

    @commands.command(aliases=get_aliases("show_aliases"))
    async def show_aliases(self, ctx):
        """Показывает все алиасы команд"""
        from utils.aliases import get_all_aliases_formatted
        text = get_all_aliases_formatted()
        await ctx.send(text)

    @commands.command(aliases=get_aliases("botstat"))
    async def botstat(self, ctx):
        """Подробная статистика бота с графиком"""
        import psutil
        import matplotlib.pyplot as plt
        from io import BytesIO
        import os

        # ==================== Сбор данных ====================
        process = psutil.Process(os.getpid())
        
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram_usage = process.memory_info().rss / 1024 / 1024  # MB
        ram_total = psutil.virtual_memory().total / 1024 / 1024
        ram_percent = psutil.virtual_memory().percent

        # Uptime
        uptime = "Неизвестно"
        if hasattr(self.bot, 'start_time'):
            delta = datetime.datetime.utcnow() - self.bot.start_time
            uptime = str(delta).split('.')[0]

        guilds = len(self.bot.guilds)
        users = sum(g.member_count for g in self.bot.guilds if g.member_count)
        latency = round(self.bot.latency * 1000, 2)

        # ==================== График ====================
        fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#0F0F1A')
        categories = ['CPU', 'RAM']
        values = [cpu_usage, ram_percent]
        colors = ['#FF69B4', '#00FFAA']

        bars = ax.bar(categories, values, color=colors, alpha=0.9)
        ax.set_ylabel('Загрузка (%)', color='white')
        ax.set_ylim(0, 100)
        ax.set_facecolor('#0F0F1A')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{height:.1f}%', ha='center', color='white', fontweight='bold')

        plt.title('Нагрузка бота', color='white', fontsize=16, pad=20)
        plt.tight_layout()

        # Сохраняем график
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
        buffer.seek(0)
        plt.close()

        # ==================== Embed ====================
        embed = discord.Embed(
            title=get_message("basic", "botstat_title"),
            color=0xFF69B4,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name=get_message("basic", "botstat_uptime"),
            value=f"`{uptime}`", 
            inline=False
        )
        embed.add_field(
            name=get_message("basic", "botstat_ping"),
            value=f"`{latency} ms`", 
            inline=True
        )
        embed.add_field(
            name=get_message("basic", "botstat_guilds"),
            value=f"`{guilds}`", 
            inline=True
        )
        embed.add_field(
            name=get_message("basic", "botstat_users"),
            value=f"`{users}`", 
            inline=True
        )
        embed.add_field(
            name=get_message("basic", "botstat_cpu"),
            value=f"`{cpu_usage:.1f}%`", 
            inline=True
        )
        embed.add_field(
            name=get_message("basic", "botstat_ram"),
            value=f"`{ram_usage:.1f} / {ram_total:.0f} MB` ({ram_percent:.1f}%)", 
            inline=True
        )

        embed.set_image(url="attachment://stats.png")
        embed.set_footer(text=get_message("basic", "botstat_footer"))

        await ctx.send(embed=embed, file=discord.File(buffer, filename="stats.png"))


async def setup(bot):
    await bot.add_cog(Basic(bot))