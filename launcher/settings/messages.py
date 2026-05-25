# launcher/settings/messages.py
import customtkinter as ctk
import os
import json
from tkinter import messagebox

from launcher.utils.path import get_messages_path


class MessagesSettings(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="transparent")
        self.ui = ui
        self.current_messages_section = None

        # === ИСПРАВЛЕННЫЙ ПУТЬ ===
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.messages_path = os.path.join(self.base_dir, "launcher", "data", "bot_messages.json")
        
        print(f"🔍 Ищем bot_messages.json по пути: {self.messages_path}")

        self.bot_messages = {}
        self.load_bot_messages()
        self.setup()

    def load_bot_messages(self):
        try:
            if os.path.exists(self.messages_path):
                with open(self.messages_path, "r", encoding="utf-8") as f:
                    self.bot_messages = json.load(f)
                print(f"✅ bot_messages.json загружен: {self.messages_path}")
            else:
                print(f"❌ bot_messages.json не найден: {self.messages_path}")
                self.bot_messages = {}
        except Exception as e:
            print(f"❌ Ошибка загрузки сообщений: {e}")
            self.bot_messages = {}

    def save_bot_messages(self):
        try:
            os.makedirs(os.path.dirname(self.messages_path), exist_ok=True)
            with open(self.messages_path, "w", encoding="utf-8") as f:
                json.dump(self.bot_messages, f, ensure_ascii=False, indent=2)
            self.ui.log_to_current_panel("✅ bot_messages.json успешно сохранён", "SUCCESS")
            messagebox.showinfo("Успешно", "Все изменения сохранены!")
            if self.current_messages_section:
                self.show_messages_section(self.current_messages_section)
            return True
        except Exception as e:
            self.ui.log_to_current_panel(f"❌ Ошибка сохранения: {e}", "ERROR")
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")
            return False

    def setup(self):
        ctk.CTkLabel(self, text="💬 Сообщения бота", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=22, weight="bold"),
                    text_color="#ff00c8").pack(pady=20)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        if not self.bot_messages:
            ctk.CTkLabel(scroll, text="bot_messages.json пуст или не найден", 
                        text_color="#ff3366").pack(pady=50)
            return

        for section_key in sorted(self.bot_messages.keys()):
            title = self.get_section_title(section_key)
            content = self.bot_messages[section_key]
            count = len(content) if isinstance(content, (dict, list)) else 0

            btn = ctk.CTkButton(scroll, 
                               text=f"{title}  ({count})",
                               height=55,
                               fg_color="#1a1a2e", 
                               hover_color="#2a2a44",
                               text_color="#e0f8ff",
                               font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                               command=lambda k=section_key: self.show_messages_section(k))
            btn.pack(pady=6, padx=10, fill="x")

    def show_messages_section(self, section_key: str):
        self.current_messages_section = section_key
        for widget in self.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=15, padx=25)

        title = self.get_section_title(section_key)
        ctk.CTkLabel(header, text=f"💬 {title}", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"),
                    text_color="#ff00c8").pack(anchor="w", side="left")

        back_btn = ctk.CTkButton(header, text="← Назад", width=120, height=38,
                                fg_color="#555555", hover_color="#666666",
                                command=self.back_to_main)
        back_btn.pack(side="right")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=10)

        save_btn = ctk.CTkButton(scroll, text="💾 СОХРАНИТЬ ВСЕ ИЗМЕНЕНИЯ", 
                                fg_color="#00ffaa", text_color="#000000", height=45,
                                font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                                command=self.save_bot_messages)
        save_btn.pack(pady=(0, 15), fill="x")

        content = self.bot_messages.get(section_key, {})

        if isinstance(content, list):
            self.create_list_editor(scroll, section_key, content)
        elif isinstance(content, dict):
            self.create_dict_editor(scroll, section_key, content)

    def back_to_main(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.setup()

    def get_section_title(self, section_key: str) -> str:
        titles = {
            "templates": "Шаблоны сообщений",
            "funny_responses": "Весёлые ответы",
            "welcome": "Приветственные сообщения",
            "errors": "Сообщения об ошибках",
            "logs": "Логи событий",
            "status": "Статусные сообщения",
            "on_command": "Сообщения при выполнении команд"
        }
        return titles.get(section_key, section_key.replace("_", " ").title())

    # === Редакторы (те же, что раньше) ===
    def create_list_editor(self, parent, section_key, items):
        for i, item in enumerate(items):
            row = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=8)
            row.pack(fill="x", pady=6, padx=5)
            entry = ctk.CTkEntry(row, height=32)
            entry.pack(side="left", fill="x", expand=True, padx=10)
            entry.insert(0, str(item))
            ctk.CTkButton(row, text="Сохранить", width=100, fg_color="#00cc88",
                         command=lambda idx=i, ent=entry, sec=section_key: 
                         self.save_list_item(sec, idx, ent.get())).pack(side="right", padx=8)

    def create_dict_editor(self, parent, section_key, data):
        for key, value in data.items():
            row = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=8)
            row.pack(fill="x", pady=8, padx=5)

            ctk.CTkLabel(row, text=key, width=160, anchor="w",
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=12)

            if isinstance(value, list):
                self.create_variants_editor(row, section_key, key, value)
            else:
                self.create_single_value_editor(row, section_key, key, value)

    def create_single_value_editor(self, parent_row, section_key, key, value):
        entry = ctk.CTkEntry(parent_row, height=32)
        entry.pack(side="left", fill="x", expand=True, padx=8)
        entry.insert(0, str(value))

        ctk.CTkButton(parent_row, text="Сохранить", width=100, fg_color="#00cc88",
                     command=lambda k=key, ent=entry, sec=section_key: 
                     self.save_single(sec, k, ent.get())).pack(side="right", padx=5)

        ctk.CTkButton(parent_row, text="+ Варианты", width=110, fg_color="#ff00c8",
                     command=lambda: self.convert_to_variants(section_key, key)).pack(side="right", padx=5)

    def create_variants_editor(self, parent_row, section_key, key, variants):
        frame = ctk.CTkFrame(parent_row, fg_color="#111118", corner_radius=8)
        frame.pack(side="left", fill="x", expand=True, padx=8)

        for i, variant in enumerate(variants):
            var_row = ctk.CTkFrame(frame, fg_color="transparent")
            var_row.pack(fill="x", pady=3)

            entry = ctk.CTkEntry(var_row, height=28)
            entry.pack(side="left", fill="x", expand=True, padx=(0,4))
            entry.insert(0, variant)

            ctk.CTkButton(var_row, text="💾", width=34, fg_color="#00cc88",
                         command=lambda idx=i, ent=entry, k=key, sec=section_key: 
                         self.save_variant(sec, k, idx, ent.get())).pack(side="left", padx=2)
            ctk.CTkButton(var_row, text="✕", width=34, fg_color="#ff3366",
                         command=lambda idx=i, k=key, sec=section_key: 
                         self.remove_variant(sec, k, idx)).pack(side="left", padx=2)

        ctk.CTkButton(frame, text="+ Добавить вариант", fg_color="#ff00c8", height=32,
                     command=lambda: self.add_variant(section_key, key)).pack(pady=6)

    def save_single(self, section_key, key, value):
        self.bot_messages[section_key][key] = value
        self.ui.log_to_current_panel(f"Сохранено: {key}", "SUCCESS")

    def save_variant(self, section_key, key, index, value):
        self.bot_messages[section_key][key][index] = value

    def save_list_item(self, section_key, index, value):
        self.bot_messages[section_key][index] = value

    def add_variant(self, section_key, key):
        if not isinstance(self.bot_messages.get(section_key, {}).get(key), list):
            self.bot_messages[section_key][key] = [self.bot_messages[section_key][key]]
        self.bot_messages[section_key][key].append("Новый вариант...")
        self.show_messages_section(section_key)

    def remove_variant(self, section_key, key, index):
        if len(self.bot_messages[section_key][key]) > 1:
            self.bot_messages[section_key][key].pop(index)
            self.show_messages_section(section_key)

    def convert_to_variants(self, section_key, key):
        current = self.bot_messages[section_key][key]
        if not isinstance(current, list):
            self.bot_messages[section_key][key] = [current]
        self.show_messages_section(section_key)