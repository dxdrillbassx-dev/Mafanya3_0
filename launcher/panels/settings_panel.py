import customtkinter as ctk
import os
from dotenv import load_dotenv

from launcher.settings.basic import BasicSettings
from launcher.settings.discord import DiscordSettings
from launcher.settings.ai import AISettings
from launcher.settings.services import ServicesSettings
from launcher.settings.messages import MessagesSettings
from launcher.settings.launcher import LauncherSettings


class SettingsPanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a0f")
        self.ui = ui
        self.current_category = None
        self.panels = {}

        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.env_path = os.path.join(self.base_dir, ".env")
        load_dotenv(self.env_path, override=True)

        self.setup()

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Левая колонка
        left_frame = ctk.CTkFrame(main_content, fg_color="#111118", width=360, corner_radius=16)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="⚙️ НАСТРОЙКИ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=20, weight="bold"), 
                    text_color="#ff00c8").pack(pady=(25, 15), anchor="w", padx=25)

        categories = [
            ("🌐 Основные", "basic"),
            ("🔑 Discord", "discord"),
            ("🧠 AI Сервисы", "ai"),
            ("🌍 Внешние Сервисы", "services"),
            ("💬 Сообщения бота", "messages"),
            ("🎨 Лаунчер", "launcher"),
        ]

        for name, key in categories:
            self.create_category_button(left_frame, name, key)

        # Правая колонка
        self.right_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.panels = {
            "basic": BasicSettings(self.right_frame, self.ui),
            "discord": DiscordSettings(self.right_frame, self.ui),
            "ai": AISettings(self.right_frame, self.ui),
            "services": ServicesSettings(self.right_frame, self.ui),
            "messages": MessagesSettings(self.right_frame, self.ui),
            "launcher": LauncherSettings(self.right_frame, self.ui),
        }

        self.show_category("basic")

    def create_category_button(self, parent, display_name, cat_key):
        btn = ctk.CTkButton(parent, text=display_name, height=52,
                           fg_color="#1a1a2e", hover_color="#2a2a44",
                           text_color="#e0f8ff", anchor="w", corner_radius=12,
                           font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"))
        btn.configure(command=lambda k=cat_key: self.show_category(k))
        btn.pack(pady=6, padx=20, fill="x")

    def show_category(self, category_key: str):
        self.current_category = category_key

        for panel in self.panels.values():
            panel.pack_forget()

        panel = self.panels.get(category_key)
        if panel:
            panel.pack(fill="both", expand=True)