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
        # Основная сетка окна
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ====================== ВЕРХНЯЯ СТРОКА ПУТИ ======================
        path_frame = ctk.CTkFrame(self, fg_color="#111118", height=60)
        path_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 0))
        path_frame.pack_propagate(False)

        ctk.CTkLabel(path_frame, text="MAFANYA 3.0", 
                    font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
                    text_color="#ff00ff").pack(side="left", padx=20)

        ctk.CTkLabel(path_frame, text="→", 
                    font=ctk.CTkFont(size=24), 
                    text_color="#666666").pack(side="left", padx=8)

        self.path_label = ctk.CTkLabel(path_frame, text="main", 
                    font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
                    text_color="#00ffff")
        self.path_label.pack(side="left", padx=8)

        # ====================== ОСНОВНОЙ БЛОК ======================
        main_block = ctk.CTkFrame(self, fg_color="#0a0a0f", corner_radius=12)
        main_block.grid(row=1, column=0, sticky="nsew", padx=14, pady=(10, 14))

        main_block.grid_columnconfigure(0, weight=0)   # Навигация
        main_block.grid_columnconfigure(1, weight=1)   # Контент
        main_block.grid_rowconfigure(0, weight=1)

        # --- Левая панель: Навигация ---
        self.sidebar = ctk.CTkFrame(main_block, width=290, fg_color="#111118", corner_radius=10)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(12, 8), pady=12)
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="📁 РАЗДЕЛЫ", 
                    font=ctk.CTkFont(size=15, weight="bold"), 
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
                              font=ctk.CTkFont(family="Consolas", size=14))  # ← исправлено
            btn.configure(command=lambda k=key: self.switch_panel(k))
            btn.pack(pady=5, padx=16, fill="x")

        # --- Правая область: Контент ---
        self.content_frame = ctk.CTkFrame(main_block, fg_color="#0a0a12", corner_radius=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 12), pady=12)

        # Создаём панели
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
                        font=ctk.CTkFont(size=32, weight="bold"), 
                        text_color="#ff00ff").pack(pady=100)
            ctk.CTkLabel(placeholder, text="Раздел находится в разработке", 
                        font=ctk.CTkFont(size=16), 
                        text_color="#8888ff").pack()
            self.current_panel = placeholder

        # Обновляем путь сверху
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