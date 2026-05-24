import customtkinter as ctk
from utils.aliases import COMMAND_ALIASES
import json
import os

class CommandsPanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a0f")
        self.ui = ui
        self.current_category = None
        self.disabled_commands = self.load_disabled_commands()
        self.setup()

    def load_disabled_commands(self):
        try:
            if os.path.exists("disabled_commands.json"):
                with open("disabled_commands.json", "r", encoding="utf-8") as f:
                    return set(json.load(f))
            return set()
        except:
            return set()

    def save_disabled_commands(self):
        try:
            with open("disabled_commands.json", "w", encoding="utf-8") as f:
                json.dump(list(self.disabled_commands), f, ensure_ascii=False, indent=2)
            self.ui.log_to_current_panel("✅ Настройки команд сохранены", "SUCCESS")
        except Exception as e:
            self.ui.log_to_current_panel(f"Ошибка сохранения: {e}", "ERROR")

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Левая панель — категории
        left_frame = ctk.CTkFrame(main_content, fg_color="#111118", width=360, corner_radius=16)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="📁 КОМАНДЫ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=20, weight="bold"), 
                    text_color="#ff00c8").pack(pady=(25, 15), anchor="w", padx=25)

        # Категории
        category_map = {
            "BASIC": ["ping", "hello", "about", "clear", "userinfo", "myid", "show_aliases", "botstat", "tech"],
            "FORZA": ["forza_status", "forzaprofile"],
            "VOICE AI": ["join_voice", "leave_voice", "tts"],
            "VOICE STT": ["start_listen", "stop_listen", "record_voice"],
            "CUSTOM ROLE": ["createrole", "listcustomroles"],
            "FUN": ["meme", "eightball"],
            "MODERATION": ["ban", "kick", "mute", "unmute"],
            "PHOTO": ["pinterest", "vkphoto"],
            "AUDIO": ["play", "skip", "pause", "resume", "leave"],
            "RELOAD": ["reload", "restart", "load", "unload", "reload_all"],
        }

        categories = {
            "🌍 basic": "BASIC",
            "🏎️ forza": "FORZA",
            "🎙️ voice_ai": "VOICE AI",
            "🎤 voice_stt": "VOICE STT",
            "👑 custom_role": "CUSTOM ROLE",
            "🎲 fun": "FUN",
            "🛡️ moderation": "MODERATION",
            "🖼️ photo": "PHOTO",
            "🎵 audio": "AUDIO",
            "🔄 reload": "RELOAD",
        }

        for display_name, cat_key in categories.items():
            count = len(category_map.get(cat_key, []))
            self.create_category_button(left_frame, display_name, cat_key, count)

        # Правая панель
        self.right_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=16)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.show_category("BASIC")

    def create_category_button(self, parent, display_name, cat_key, count):
        btn_frame = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=12, height=52)
        btn_frame.pack(pady=6, padx=20, fill="x")
        btn_frame.pack_propagate(False)

        name_label = ctk.CTkLabel(btn_frame, text=display_name, 
                                 font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                                 text_color="#e0f8ff", anchor="w")
        name_label.pack(side="left", padx=22, pady=12)

        count_label = ctk.CTkLabel(btn_frame, text=str(count), 
                                  font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                                  text_color="#ff00c8")
        count_label.pack(side="right", padx=22, pady=12)

        # Кликабельность всей области
        for widget in (btn_frame, name_label, count_label):
            widget.bind("<Button-1>", lambda e, k=cat_key: self.show_category(k))
            widget.bind("<Enter>", lambda e: btn_frame.configure(fg_color="#2a2a44"))
            widget.bind("<Leave>", lambda e: btn_frame.configure(fg_color="#1a1a2e"))

    def show_category(self, category_key: str):
        self.current_category = category_key
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header.pack(fill="x", pady=15, padx=25)

        ctk.CTkLabel(header, text=f"/commands/{category_key.lower()}", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=16, weight="bold"),
                    text_color="#ff00c8").pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=10)

        category_map = {
            "BASIC": ["ping", "hello", "about", "clear", "userinfo", "myid", "show_aliases", "botstat", "tech"],
            "FORZA": ["forza_status", "forzaprofile"],
            "VOICE AI": ["join_voice", "leave_voice", "tts"],
            "VOICE STT": ["start_listen", "stop_listen", "record_voice"],
            "CUSTOM ROLE": ["createrole", "listcustomroles"],
            "FUN": ["meme", "eightball"],
            "MODERATION": ["ban", "kick", "mute", "unmute"],
            "PHOTO": ["pinterest", "vkphoto"],
            "AUDIO": ["play", "skip", "pause", "resume", "leave"],
            "RELOAD": ["reload", "restart", "load", "unload", "reload_all"],
        }

        for cmd in sorted(category_map.get(category_key, [])):
            self.create_command_row(scroll, cmd)

    def get_short_aliases(self, cmd_name):
        aliases = COMMAND_ALIASES.get(cmd_name, [])
        if not aliases:
            return ""
        if len(aliases) == 1:
            return f"[{aliases[0]}]"
        else:
            return f"[{aliases[0]}, ...]"

    def create_command_row(self, parent, cmd_name):
        is_disabled = cmd_name in self.disabled_commands

        cmd_frame = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=12, height=68)
        cmd_frame.pack(fill="x", pady=6, padx=5)
        cmd_frame.pack_propagate(False)

        ctk.CTkLabel(cmd_frame, text=f"!{cmd_name}", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=16, weight="bold"),
                    text_color="#ffff80").pack(side="left", padx=22, pady=12)

        alias_str = self.get_short_aliases(cmd_name)
        if alias_str:
            ctk.CTkLabel(cmd_frame, text=alias_str, 
                        font=ctk.CTkFont(family="IBM Plex Mono", size=12),
                        text_color="#88ddff").pack(side="left", padx=10, pady=12)

        btn_frame = ctk.CTkFrame(cmd_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=20)

        toggle_icon = "🔴" if is_disabled else "🟢"
        toggle_color = "#ff3366" if is_disabled else "#00ffaa"
        
        toggle_btn = ctk.CTkButton(btn_frame, text=toggle_icon, width=48, height=48,
                                  corner_radius=12, fg_color=toggle_color, 
                                  hover_color="#2a2a44", font=ctk.CTkFont(size=20),
                                  command=lambda c=cmd_name: self.toggle_command(c))
        toggle_btn.pack(side="left", padx=5)

        info_btn = ctk.CTkButton(btn_frame, text="ℹ", width=48, height=48,
                                corner_radius=12, fg_color="#6666ff", 
                                hover_color="#5555cc", font=ctk.CTkFont(size=18, weight="bold"),
                                command=lambda c=cmd_name: self.show_command_info(c))
        info_btn.pack(side="left", padx=5)

    def toggle_command(self, cmd_name):
        if cmd_name in self.disabled_commands:
            self.disabled_commands.remove(cmd_name)
        else:
            self.disabled_commands.add(cmd_name)
        
        self.save_disabled_commands()
        self.show_category(self.current_category)

    def show_command_info(self, cmd_name):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.right_frame, fg_color="#111118", corner_radius=16)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(main_frame, text=f"КОМАНДА: !{cmd_name.upper()}", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=24, weight="bold"),
                    text_color="#ffff80").pack(pady=(30, 10))

        status = "🔴 ОТКЛЮЧЕНА" if cmd_name in self.disabled_commands else "🟢 АКТИВНА"
        status_color = "#ff3366" if "ОТКЛ" in status else "#00ffaa"
        ctk.CTkLabel(main_frame, text=status, 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=16, weight="bold"),
                    text_color=status_color).pack(pady=(0, 30))

        # Алиасы
        alias_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a2e", corner_radius=12)
        alias_frame.pack(fill="x", pady=15, padx=25)

        ctk.CTkLabel(alias_frame, text="АЛИАСЫ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=15, weight="bold"),
                    text_color="#ff00c8").pack(anchor="w", padx=20, pady=(15, 8))

        self.alias_container = ctk.CTkFrame(alias_frame, fg_color="transparent")
        self.alias_container.pack(fill="x", padx=20, pady=(0, 10))

        self.current_aliases = COMMAND_ALIASES.get(cmd_name, []).copy()
        self.cmd_name_for_edit = cmd_name

        self.refresh_aliases_display()

        add_frame = ctk.CTkFrame(alias_frame, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(5, 15))

        self.alias_entry = ctk.CTkEntry(add_frame, placeholder_text="Новый алиас...", height=32)
        self.alias_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        add_btn = ctk.CTkButton(add_frame, text="+ Добавить", width=120, height=32,
                               fg_color="#ff00c8", command=self.add_alias)
        add_btn.pack(side="right")

        # Информация
        info_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a2e", corner_radius=12)
        info_frame.pack(fill="x", pady=15, padx=25)

        ctk.CTkLabel(info_frame, text="ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                    text_color="#ff00c8").pack(anchor="w", padx=20, pady=(15, 8))

        details = [
            ("Категория", self.current_category),
            ("Основная команда", f"!{cmd_name}"),
        ]

        for label, value in details:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(row, text=label + ":", 
                        font=ctk.CTkFont(family="IBM Plex Mono", size=13, weight="bold"),
                        text_color="#aaaaaa", width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, 
                        font=ctk.CTkFont(family="IBM Plex Mono", size=13),
                        text_color="#e0f8ff").pack(side="left")

        back_btn = ctk.CTkButton(main_frame, text="← НАЗАД К СПИСКУ КОМАНД", 
                                fg_color="#ff00c8", height=55,
                                font=ctk.CTkFont(family="IBM Plex Mono", size=15, weight="bold"),
                                command=lambda: self.show_category(self.current_category))
        back_btn.pack(pady=30)

    def refresh_aliases_display(self):
        for widget in self.alias_container.winfo_children():
            widget.destroy()

        for alias in self.current_aliases:
            tag = ctk.CTkFrame(self.alias_container, fg_color="#2a2a44", corner_radius=8)
            tag.pack(side="left", padx=4, pady=4)

            ctk.CTkLabel(tag, text=alias, 
                        font=ctk.CTkFont(family="IBM Plex Mono", size=13),
                        text_color="#ffffff").pack(side="left", padx=(10, 6), pady=6)

            remove_btn = ctk.CTkButton(tag, text="✕", width=20, height=20,
                                      fg_color="#ff3366", hover_color="#cc2233",
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      command=lambda a=alias: self.remove_alias(a))
            remove_btn.pack(side="right", padx=(0, 6), pady=4)

    def add_alias(self):
        new_alias = self.alias_entry.get().strip().lower()
        if new_alias and new_alias not in self.current_aliases:
            self.current_aliases.append(new_alias)
            self.refresh_aliases_display()
            self.alias_entry.delete(0, "end")
            self.ui.log_to_current_panel(f"Добавлен алиас '{new_alias}' для !{self.cmd_name_for_edit}", "SUCCESS")

    def remove_alias(self, alias):
        if alias in self.current_aliases:
            self.current_aliases.remove(alias)
            self.refresh_aliases_display()
            self.ui.log_to_current_panel(f"Удалён алиас '{alias}' для !{self.cmd_name_for_edit}", "SYSTEM")