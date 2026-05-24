import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from launcher.config import TITLE, GEOMETRY
from launcher.core import BotCore
from launcher.panels.main_panel import MainPanel
from launcher.panels.commands_panel import CommandsPanel
from launcher.panels.maintenance_panel import MaintenancePanel


class RetroLauncherUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # === ПИКСЕЛЬНЫЙ RETRO ШРИФТ ===
        self.pixel_font = ctk.CTkFont(family="Consolas", size=14, weight="bold")
        self.pixel_font_small = ctk.CTkFont(family="Consolas", size=12, weight="bold")
        self.pixel_font_big = ctk.CTkFont(family="Consolas", size=20, weight="bold")
        self.pixel_font_title = ctk.CTkFont(family="Consolas", size=24, weight="bold")

        self.title(TITLE)
        self.geometry(GEOMETRY)
        self.resizable(False, False)

        self.core = BotCore()
        self.full_maintenance_mode = False
        self.current_panel = None
        self.panels = {}
        self.path_label = None

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ====================== ВЕРХНИЙ ПУТЬ ======================
        path_frame = ctk.CTkFrame(self, fg_color="#111118", height=64)
        path_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 0))
        path_frame.pack_propagate(False)

        ctk.CTkLabel(path_frame, text="MAFANYA 3.0", 
                    font=self.pixel_font_title,
                    text_color="#ff00ff").pack(side="left", padx=22)

        ctk.CTkLabel(path_frame, text="→", 
                    font=ctk.CTkFont(family="Consolas", size=28), 
                    text_color="#555555").pack(side="left", padx=8)

        self.path_label = ctk.CTkLabel(path_frame, text="main", 
                    font=self.pixel_font_title,
                    text_color="#00ffff")
        self.path_label.pack(side="left", padx=8)

        # ====================== ОСНОВНОЙ БЛОК ======================
        main_block = ctk.CTkFrame(self, fg_color="#0a0a0f", corner_radius=12)
        main_block.grid(row=1, column=0, sticky="nsew", padx=14, pady=(10, 14))

        main_block.grid_columnconfigure(0, weight=0)
        main_block.grid_columnconfigure(1, weight=1)
        main_block.grid_rowconfigure(0, weight=1)

        # Левая колонка
        left_column = ctk.CTkFrame(main_block, fg_color="transparent", width=290)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(12, 8), pady=12)

        # Навигатор
        self.sidebar = ctk.CTkFrame(left_column, fg_color="#111118", corner_radius=10)
        self.sidebar.pack(fill="both", expand=True, pady=(0, 8))

        ctk.CTkLabel(self.sidebar, text="📁 РАЗДЕЛЫ", 
                    font=self.pixel_font_big,
                    text_color="#00ffcc").pack(pady=(20, 12), anchor="w", padx=20)

        nav = [
            ("🌐 Главная", "main"),
            ("📜 Команды", "commands"),
            ("🔧 Техрежим", "maintenance"),
            ("📊 Статистика", "stats"),
            ("⚙️ Настройки", "settings"),
        ]

        for text, key in nav:
            btn = ctk.CTkButton(self.sidebar, text=text, height=50,
                              fg_color="#1a1a2e",
                              hover_color="#2a2a44",
                              text_color="#e0e0ff",
                              anchor="w",
                              corner_radius=8,
                              font=self.pixel_font)
            btn.configure(command=lambda k=key: self.switch_panel(k))
            btn.pack(pady=6, padx=16, fill="x")

        # Инфо блок внизу
        info_frame = ctk.CTkFrame(left_column, fg_color="#111118", height=68, corner_radius=10)
        info_frame.pack(fill="x", side="bottom", pady=(8, 0))
        info_frame.pack_propagate(False)

        ctk.CTkLabel(info_frame, text="v3.0", 
                    font=self.pixel_font,
                    text_color="#00ffff").pack(pady=(12, 1))

        ctk.CTkLabel(info_frame, text="by dxdrillbassx", 
                    font=self.pixel_font_small,
                    text_color="#8888ff").pack(pady=(0, 10))

        # ====================== КОНТЕНТ ======================
        self.content_frame = ctk.CTkFrame(main_block, fg_color="#0a0a12", corner_radius=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 12), pady=12)

        self.panels["main"] = MainPanel(self.content_frame, self)
        self.panels["commands"] = CommandsPanel(self.content_frame, self)
        self.panels["maintenance"] = MaintenancePanel(self.content_frame, self)

        self.switch_panel("main")

    def switch_panel(self, panel_name: str):
        if self.current_panel:
            self.current_panel.pack_forget()

        panel = self.panels.get(panel_name)

        if panel:
            panel.pack(fill="both", expand=True)
            self.current_panel = panel
        else:
            placeholder = ctk.CTkFrame(self.content_frame, fg_color="#0a0a12")
            placeholder.pack(fill="both", expand=True)
            ctk.CTkLabel(placeholder, text=panel_name.upper(), 
                        font=self.pixel_font_title, 
                        text_color="#ff00ff").pack(pady=120)
            ctk.CTkLabel(placeholder, text="Раздел находится в разработке", 
                        font=self.pixel_font, 
                        text_color="#8888ff").pack()
            self.current_panel = placeholder

        display = {"main": "main", "commands": "commands", 
                  "maintenance": "maintenance", "stats": "stats", 
                  "settings": "settings"}.get(panel_name, panel_name)
        self.path_label.configure(text=display)

        self.log_to_current_panel(f"Открыта панель: {panel_name}", "UI")

    # ====================== ОБЩИЕ МЕТОДЫ ======================
    def toggle_bot(self):
        if not self.core.is_running:
            success, msg = self.core.start_bot()
            if success:
                self.update_start_button(True)
            self.log_to_current_panel(msg, "SUCCESS" if success else "ERROR")
        else:
            success, msg = self.core.stop_bot()
            if success:
                self.update_start_button(False)
            self.log_to_current_panel(msg, "SYSTEM")

    def update_start_button(self, running: bool):
        try:
            main_panel = self.panels.get("main")
            if main_panel and hasattr(main_panel, 'start_btn'):
                if running:
                    main_panel.start_btn.configure(text="■ ОСТАНОВИТЬ БОТА", fg_color="#ff3366")
                    main_panel.status_label.configure(text="ONLINE", text_color="#00ff88")
                else:
                    main_panel.start_btn.configure(text="▶ ЗАПУСТИТЬ БОТА", fg_color="#00ff88")
                    main_panel.status_label.configure(text="OFFLINE", text_color="#ff4444")
        except:
            pass

    def toggle_maintenance(self):
        self.full_maintenance_mode = not self.full_maintenance_mode
        status = "🚨 ПОЛНЫЙ ТЕХРЕЖИМ ВКЛЮЧЁН" if self.full_maintenance_mode else "🟢 ТЕХРЕЖИМ ВЫКЛЮЧЕН"
        self.log_to_current_panel(status, "CRITICAL" if self.full_maintenance_mode else "SYSTEM")

    def log_to_current_panel(self, message: str, prefix="INFO"):
        try:
            if hasattr(self.current_panel, 'log'):
                self.current_panel.log(message, prefix)
        except:
            pass

    def run(self):
        self.mainloop()