import customtkinter as ctk
import os


class DiscordSettings(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="transparent")
        self.ui = ui
        self.setup()

    def setup(self):
        ctk.CTkLabel(self, text="🔑 Discord Настройки", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=24, weight="bold"),
                    text_color="#ff00c8").pack(pady=30)

        # Пример строк
        settings = [
            ("OWNER_ID", os.getenv("OWNER_ID", "Не задан")),
            ("ROLE_ID", os.getenv("ROLE_ID", "Не задан")),
            ("LOG_CHANNEL_ID", os.getenv("LOG_CHANNEL_ID", "Не задан")),
            ("WELCOME_CHANNEL_ID", os.getenv("WELCOME_CHANNEL_ID", "Не задан")),
        ]

        for name, value in settings:
            frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12, height=60)
            frame.pack(fill="x", padx=40, pady=8)
            frame.pack_propagate(False)

            ctk.CTkLabel(frame, text=name, width=200, anchor="w",
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=20)
            ctk.CTkLabel(frame, text=value, text_color="#88ddff").pack(side="left")