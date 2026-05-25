import customtkinter as ctk
import sys
import os
import launcher.ui

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from launcher.config import TITLE, GEOMETRY
from launcher.core import BotCore
from launcher.panels.main_panel import MainPanel
from launcher.panels.commands_panel import CommandsPanel
from launcher.panels.maintenance_panel import MaintenancePanel
from launcher.panels.chats_panel import ChatsPanel
from launcher.panels.settings_panel import SettingsPanel


class RetroLauncherUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ==================== COBALT + PINK THEME ====================
        self.ACCENT = "#ff00c8"        # Ярко-розовый
        self.ACCENT_DARK = "#d100a8"   # Hover
        self.BG = "#0a0a0f"
        self.SURFACE = "#111118"
        self.SURFACE2 = "#1a1a2e"
        self.TEXT = "#e0f8ff"
        self.TEXT_SECONDARY = "#a0ddff"
        self.SUCCESS = "#00ffaa"
        self.ERROR = "#ff3366"

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # ==================== ШРИФТЫ ====================
        self.main_font = ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold")
        self.small_font = ctk.CTkFont(family="IBM Plex Mono", size=12, weight="bold")
        self.big_font = ctk.CTkFont(family="IBM Plex Mono", size=20, weight="bold")
        self.title_font = ctk.CTkFont(family="IBM Plex Mono", size=24, weight="bold")

        self.title(TITLE)
        self.geometry(GEOMETRY)
        self.resizable(False, False)

        self.core = BotCore()
        self.core.set_ui_callback(self.log_to_current_panel)

        launcher.ui.launcher_instance = self

        self.full_maintenance_mode = False
        self.current_panel = None
        self.panels = {}
        self.path_label = None
        self.active_button = None  # Для выделения текущего раздела

        self.setup_ui()

    def setup_ui(self):
        self.configure(fg_color=self.BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Верхний путь
        path_frame = ctk.CTkFrame(self, fg_color=self.SURFACE, height=64)
        path_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 0))
        path_frame.pack_propagate(False)

        ctk.CTkLabel(path_frame, text="MAFANYA 3.0", 
                    font=self.title_font, text_color=self.ACCENT).pack(side="left", padx=22)

        ctk.CTkLabel(path_frame, text="→", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=28), text_color="#555555").pack(side="left", padx=8)

        self.path_label = ctk.CTkLabel(path_frame, text="main", 
                    font=self.title_font, text_color=self.TEXT)
        self.path_label.pack(side="left", padx=8)

        # Основной блок
        main_block = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=12)
        main_block.grid(row=1, column=0, sticky="nsew", padx=14, pady=(10, 14))

        main_block.grid_columnconfigure(0, weight=0)
        main_block.grid_columnconfigure(1, weight=1)
        main_block.grid_rowconfigure(0, weight=1)

        # Левая колонка
        left_column = ctk.CTkFrame(main_block, fg_color="transparent", width=290)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(12, 8), pady=12)

        self.sidebar = ctk.CTkFrame(left_column, fg_color=self.SURFACE, corner_radius=10)
        self.sidebar.pack(fill="both", expand=True, pady=(0, 8))

        ctk.CTkLabel(self.sidebar, text="📁 РАЗДЕЛЫ", 
                    font=self.big_font, text_color=self.ACCENT).pack(pady=(20, 12), anchor="w", padx=20)

        self.nav_buttons = {}  # Сохраняем кнопки для выделения

        nav = [
            ("🌐 Главная", "main"),
            ("📜 Команды", "commands"),
            ("💬 Чаты", "chats"),
            ("🔧 Техрежим", "maintenance"),
            ("⚙️ Настройки", "settings"),
        ]

        for text, key in nav:
            btn = ctk.CTkButton(self.sidebar, text=text, height=50,
                              fg_color=self.SURFACE2, 
                              hover_color=self.ACCENT_DARK,
                              text_color=self.TEXT,
                              anchor="w", 
                              corner_radius=8,
                              font=self.main_font)
            btn.configure(command=lambda k=key: self.switch_panel(k))
            btn.pack(pady=6, padx=16, fill="x")
            self.nav_buttons[key] = btn

        # Инфо внизу
        info_frame = ctk.CTkFrame(left_column, fg_color=self.SURFACE, height=68, corner_radius=10)
        info_frame.pack(fill="x", side="bottom", pady=(8, 0))
        info_frame.pack_propagate(False)

        ctk.CTkLabel(info_frame, text="v3.0", font=self.main_font, text_color=self.ACCENT).pack(pady=(12, 1))
        ctk.CTkLabel(info_frame, text="by dxdrillbassx", font=self.small_font, text_color=self.TEXT_SECONDARY).pack(pady=(0, 10))

        # Контент
        self.content_frame = ctk.CTkFrame(main_block, fg_color=self.BG, corner_radius=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 12), pady=12)

        self.panels["main"] = MainPanel(self.content_frame, self)
        self.panels["commands"] = CommandsPanel(self.content_frame, self)
        self.panels["maintenance"] = MaintenancePanel(self.content_frame, self)
        self.panels["chats"] = ChatsPanel(self.content_frame, self)
        self.panels["settings"] = SettingsPanel(self.content_frame, self)

        self.switch_panel("main")

    def force_kill_bot(self):
        """Полное убийство процесса бота"""
        success, msg = self.core.force_kill()
        self.log_to_current_panel(msg, "CRITICAL" if success else "ERROR")
        if success:
            self.update_start_button(False)

    def nuke_all_processes(self):
        """Полная ядерная очистка всех процессов"""
        self.log_to_current_panel("☢ Запущена полная очистка всех процессов Mafanya...", "CRITICAL")
        
        success, msg = self.core.kill_all_python_processes()
        self.log_to_current_panel(msg, "CRITICAL" if success else "ERROR")
        
        # Обновляем статус
        self.update_start_button(False)

    def switch_panel(self, panel_name: str):
        if self.current_panel:
            self.current_panel.pack_forget()

        panel = self.panels.get(panel_name)
        if panel:
            panel.pack(fill="both", expand=True)
            self.current_panel = panel
        else:
            placeholder = ctk.CTkFrame(self.content_frame, fg_color=self.BG)
            placeholder.pack(fill="both", expand=True)
            ctk.CTkLabel(placeholder, text=panel_name.upper(), 
                        font=self.title_font, text_color=self.ACCENT).pack(pady=120)
            ctk.CTkLabel(placeholder, text="Раздел находится в разработке", 
                        font=self.main_font, text_color=self.TEXT_SECONDARY).pack()
            self.current_panel = placeholder

        # Выделяем активную кнопку
        self.highlight_active_button(panel_name)

        display = {"main": "main", "commands": "commands", "chats": "chats",
                  "maintenance": "maintenance", "settings": "settings"}.get(panel_name, panel_name)
        self.path_label.configure(text=display)

        self.log_to_current_panel(f"Открыта панель: {panel_name}", "UI")

    def highlight_active_button(self, active_key: str):
        """Выделяет текущий раздел"""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color=self.ACCENT, text_color="#000000", hover_color=self.ACCENT_DARK)
            else:
                btn.configure(fg_color=self.SURFACE2, text_color=self.TEXT, hover_color=self.ACCENT_DARK)

    # Остальные методы
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
            if main_panel and hasattr(main_panel, 'start_btn') and hasattr(main_panel, 'status_label'):
                if running:
                    main_panel.start_btn.configure(text="■ ОСТАНОВИТЬ БОТА", fg_color=self.ERROR)
                    main_panel.status_label.configure(text="ONLINE", text_color=self.SUCCESS)
                else:
                    main_panel.start_btn.configure(text="▶ ЗАПУСТИТЬ БОТА", fg_color=self.SUCCESS)
                    main_panel.status_label.configure(text="OFFLINE", text_color=self.ERROR)
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