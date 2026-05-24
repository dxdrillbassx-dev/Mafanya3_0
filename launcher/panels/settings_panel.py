import customtkinter as ctk
import os
from tkinter import messagebox
from dotenv import load_dotenv, set_key, find_dotenv


class SettingsPanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a0f")
        self.ui = ui
        self.current_category = None
        
        # Правильный путь к .env
        self.env_path = "/home/workdir/attachments/.env"
        if not os.path.exists(self.env_path):
            self.env_path = find_dotenv()  # fallback
        
        # Загружаем .env при открытии панели
        load_dotenv(self.env_path, override=True)
        
        self.setup()

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Левая колонка — категории
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
            ("🎨 Лаунчер", "launcher"),
        ]

        for name, key in categories:
            self.create_category_button(left_frame, name, key)

        # Правая колонка
        self.right_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=16)
        self.right_frame.pack(side="right", fill="both", expand=True)

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
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header.pack(fill="x", pady=15, padx=25)

        ctk.CTkLabel(header, text=f"/settings/{category_key}", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=16, weight="bold"),
                    text_color="#ff00c8").pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=10)

        if category_key == "basic":
            self.create_setting_row(scroll, "Тема лаунчера", "dark", "LAUNCHER_THEME", is_env=False)

        elif category_key == "discord":
            self.create_setting_row(scroll, "OWNER_ID", os.getenv("OWNER_ID", "Не задан"), "OWNER_ID")
            self.create_setting_row(scroll, "ROLE_ID", os.getenv("ROLE_ID", "Не задан"), "ROLE_ID")
            self.create_setting_row(scroll, "LOG_CHANNEL_ID", os.getenv("LOG_CHANNEL_ID", "Не задан"), "LOG_CHANNEL_ID")
            self.create_setting_row(scroll, "WELCOME_CHANNEL_ID", os.getenv("WELCOME_CHANNEL_ID", "Не задан"), "WELCOME_CHANNEL_ID")

        elif category_key == "ai":
            self.create_setting_row(scroll, "XAI_API_KEY", self.mask_key(os.getenv("XAI_API_KEY", "")), "XAI_API_KEY")
            self.create_setting_row(scroll, "GEMINI_API_KEY", self.mask_key(os.getenv("GEMINI_API_KEY", "")), "GEMINI_API_KEY")

        elif category_key == "services":
            self.create_setting_row(scroll, "PINTEREST_EMAIL", os.getenv("PINTEREST_EMAIL", "Не задан"), "PINTEREST_EMAIL")
            self.create_setting_row(scroll, "VK_TOKEN", self.mask_key(os.getenv("VK_TOKEN", "")), "VK_TOKEN")
            self.create_setting_row(scroll, "FORZA_UDP_PORT", os.getenv("FORZA_UDP_PORT", "8001"), "FORZA_UDP_PORT")

        elif category_key == "launcher":
            self.create_setting_row(scroll, "Шрифт интерфейса", "IBM Plex Mono", "LAUNCHER_FONT", is_env=False)
            self.create_setting_row(scroll, "Цвет акцента", "#ff00c8", "LAUNCHER_ACCENT", is_env=False)
            self.create_setting_row(scroll, "Автоочистка логов", "Выкл", "CLEAR_LOGS", is_env=False)
            self.create_setting_row(scroll, "Размер окна", "1280x720", "GEOMETRY", is_env=False)

    def mask_key(self, key: str) -> str:
        if not key:
            return "Не задан"
        if len(key) > 15:
            return key[:8] + "••••••••" + key[-6:]
        return key

    def create_setting_row(self, parent, name: str, value: str, env_key: str, is_env: bool = True):
        frame = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=12, height=68)
        frame.pack(fill="x", pady=6, padx=5)
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text=name, 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=15, weight="bold"),
                    text_color="#ffffff").pack(side="left", padx=25, pady=12)

        value_label = ctk.CTkLabel(frame, text=value, 
                                  font=ctk.CTkFont(family="IBM Plex Mono", size=13),
                                  text_color="#88ddff")
        value_label.pack(side="left", padx=10, pady=12)

        edit_btn = ctk.CTkButton(frame, text="ИЗМЕНИТЬ", width=130, height=42,
                                fg_color="#ff00c8", hover_color="#d100a8",
                                font=ctk.CTkFont(family="IBM Plex Mono", size=12, weight="bold"),
                                command=lambda k=env_key, n=name, v=value: self.edit_setting(k, n, v, is_env))
        edit_btn.pack(side="right", padx=20)

    def edit_setting(self, env_key: str, name: str, current_value: str, is_env: bool):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        edit_frame = ctk.CTkFrame(self.right_frame, fg_color="#111118", corner_radius=16)
        edit_frame.pack(fill="both", expand=True, padx=40, pady=60)

        ctk.CTkLabel(edit_frame, text=f"Редактирование: {name}", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"),
                    text_color="#ff00c8").pack(pady=(30, 5))

        if env_key and env_key not in ["LAUNCHER_THEME", "LAUNCHER_FONT"]:
            ctk.CTkLabel(edit_frame, text=f"Ключ: {env_key}", 
                        font=ctk.CTkFont(family="IBM Plex Mono", size=13),
                        text_color="#888888").pack(anchor="w", padx=40)

        self.edit_entry = ctk.CTkEntry(edit_frame, height=50, 
                                      font=ctk.CTkFont(family="IBM Plex Mono", size=14))
        self.edit_entry.pack(pady=15, padx=40, fill="x")
        self.edit_entry.insert(0, current_value if not "••••" in str(current_value) else "")

        btn_frame = ctk.CTkFrame(edit_frame, fg_color="transparent")
        btn_frame.pack(pady=40)

        save_text = "✅ СОХРАНИТЬ В .ENV" if is_env and env_key else "✅ СОХРАНИТЬ"
        save_color = "#00ffaa" if is_env and env_key else "#ff8800"

        ctk.CTkButton(btn_frame, text=save_text, fg_color=save_color, height=55, width=220,
                     font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                     command=lambda: self.save_setting(env_key, name, is_env)).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="← ОТМЕНА", fg_color="#555555", height=55, width=180,
                     font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                     command=lambda: self.show_category(self.current_category)).pack(side="left", padx=10)

    def save_setting(self, env_key: str, name: str, is_env: bool):
        new_value = self.edit_entry.get().strip()

        if is_env and env_key:
            try:
                set_key(self.env_path, env_key, new_value)
                load_dotenv(self.env_path, override=True)
                self.ui.log_to_current_panel(f"✅ {env_key} сохранён в .env", "SUCCESS")
                messagebox.showinfo("Успешно", f"{name}\nЗначение сохранено в .env")
            except Exception as e:
                self.ui.log_to_current_panel(f"❌ Ошибка: {e}", "ERROR")
                messagebox.showerror("Ошибка", str(e))
        else:
            self.ui.log_to_current_panel(f"{name} изменён (локально)", "SYSTEM")

        self.show_category(self.current_category)

    def log(self, message: str, prefix="INFO"):
        try:
            if hasattr(self.ui.current_panel, 'log'):
                self.ui.current_panel.log(message, prefix)
        except:
            pass