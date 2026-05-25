# cogs/forza.py
import discord
from discord.ext import commands
import socket
import struct
import asyncio
import os
import json
from datetime import datetime

from utils.aliases import get_aliases
from utils.module_descriptions import get_message   # ← Главный импорт


class ForzaTelemetry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.udp_port = int(os.getenv("FORZA_UDP_PORT", 8001))

        self.sock = None
        self.running = False
        self.listener_task = None

        self.last_data = None
        self.message_to_edit = None
        self.last_car_ordinal = None

        self.car_names = self.load_car_names()

    def load_car_names(self) -> dict:
        try:
            path = "data/forza_cars.json"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cars = {}
                for k, v in data.items():
                    if str(k).isdigit():
                        ordinal = int(k)
                        name = v if isinstance(v, str) else v.get("name", f"ID {ordinal}")
                        cars[ordinal] = {"name": name}
                print(get_message("forza", "cars_loaded", count=len(cars)))
                return cars
            print(get_message("forza", "cars_not_found"))
            return {}
        except Exception as e:
            print(get_message("forza", "listener_error", error=str(e)))
            return {}

    def get_car_info(self, ordinal: int):
        return self.car_names.get(ordinal, {"name": f"Unknown Car ({ordinal})"})

    def parse_packet(self, packet: bytes):
        if len(packet) < 324:
            return None

        try:
            data = {
                "IsRaceOn": struct.unpack("<i", packet[0:4])[0],
                "CarOrdinal": struct.unpack("<i", packet[212:216])[0],

                "CurrentEngineRpm": struct.unpack("<f", packet[16:20])[0],
                "EngineMaxRpm": struct.unpack("<f", packet[8:12])[0],

                "Speed": round(struct.unpack("<f", packet[256:260])[0] * 3.6, 1),

                "Accel": struct.unpack("<B", packet[315:316])[0],
                "Brake": struct.unpack("<B", packet[316:317])[0],
                "Gear":  struct.unpack("<B", packet[319:320])[0],
                "Steer": struct.unpack("<b", packet[320:321])[0],
            }

            if data["Accel"] > 100: data["Accel"] = 0
            if data["Brake"] > 100: data["Brake"] = 0
            if data["Gear"] > 10: data["Gear"] = 0

            return data
        except:
            return None

    async def update_dashboard(self):
        if not self.last_data or not self.message_to_edit:
            return

        d = self.last_data
        car = self.get_car_info(d.get("CarOrdinal", 0))

        embed = discord.Embed(
            title=get_message("forza", "dashboard_title"),
            description=f"**{car['name']}**",
            color=0x00FF88,
            timestamp=datetime.utcnow()
        )

        rpm = int(d["CurrentEngineRpm"])
        rpm_max = max(d["EngineMaxRpm"], 1)
        rpm_percent = min(100, int((rpm / rpm_max) * 100))
        gear = d["Gear"] if d.get("Gear", 0) > 0 else "N"

        embed.add_field(
            name=get_message("forza", "speed_field"),
            value=f"**{d['Speed']} км/ч**", 
            inline=True
        )
        embed.add_field(
            name=get_message("forza", "rpm_field"),
            value=f"`{rpm} RPM` ({rpm_percent}%)", 
            inline=True
        )
        embed.add_field(
            name=get_message("forza", "gear_field"),
            value=f"**{gear}**", 
            inline=True
        )

        embed.add_field(
            name=get_message("forza", "accel_field"),
            value=f"`{d.get('Accel', 0)}%`", 
            inline=True
        )
        embed.add_field(
            name=get_message("forza", "brake_field"),
            value=f"`{d.get('Brake', 0)}%`", 
            inline=True
        )
        embed.add_field(
            name=get_message("forza", "steer_field"),
            value=f"`{d.get('Steer', 0)}`", 
            inline=True
        )

        embed.set_footer(text=get_message("forza", "dashboard_footer"))

        try:
            await self.message_to_edit.edit(embed=embed)
        except:
            self.message_to_edit = None

    def udp_listener(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.sock.bind(("0.0.0.0", self.udp_port))
            print(get_message("forza", "listener_started"))
        except Exception as e:
            print(get_message("forza", "listener_error", error=str(e)))
            return

        self.running = True

        while self.running:
            try:
                packet, _ = self.sock.recvfrom(4096)
                data = self.parse_packet(packet)

                if data and data.get("IsRaceOn") == 1:
                    current_ordinal = data.get("CarOrdinal")

                    if self.last_car_ordinal is not None and self.last_car_ordinal != current_ordinal:
                        asyncio.run_coroutine_threadsafe(
                            self.send_car_change(current_ordinal), self.bot.loop
                        )

                    self.last_data = data
                    self.last_car_ordinal = current_ordinal

                    if self.message_to_edit:
                        asyncio.run_coroutine_threadsafe(self.update_dashboard(), self.bot.loop)
            except:
                continue

    async def send_car_change(self, ordinal: int):
        car = self.get_car_info(ordinal)
        embed = discord.Embed(
            title=get_message("forza", "car_change_title"),
            description=f"**{car['name']}**",
            color=0x00FF88,
            timestamp=datetime.utcnow()
        )
        channel = self.bot.get_channel(int(os.getenv("FORZA_CHANNEL_ID", 0)))
        if channel:
            await channel.send(embed=embed)

    @commands.command(aliases=get_aliases("forza_status"))
    async def forza_status(self, ctx):
        if self.listener_task and not self.listener_task.done():
            self.running = False
            if self.sock: 
                self.sock.close()
            self.listener_task = None
            self.message_to_edit = None
            await ctx.reply(get_message("forza", "listener_stopped"))
        else:
            self.listener_task = asyncio.create_task(asyncio.to_thread(self.udp_listener))
            await ctx.reply(get_message("forza", "listener_started_command"))

    @commands.command(aliases=get_aliases("forzaprofile"))
    async def forzaprofile(self, ctx):
        if not self.listener_task or self.listener_task.done():
            await ctx.reply(get_message("forza", "listener_not_running"))
            return
        
        embed = discord.Embed(
            title=get_message("forza", "forzaprofile_title"),
            description=get_message("forza", "forzaprofile_waiting"),
            color=0xFFAA00
        )
        self.message_to_edit = await ctx.reply(embed=embed)

    async def cog_unload(self):
        self.running = False
        if self.sock: 
            self.sock.close()
        if self.listener_task: 
            self.listener_task.cancel()


async def setup(bot):
    await bot.add_cog(ForzaTelemetry(bot))
    print(get_message("forza", "cog_loaded"))