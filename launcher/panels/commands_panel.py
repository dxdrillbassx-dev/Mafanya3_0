import customtkinter as ctk
from launcher.utils.uniform_card import UniformCard
from utils.aliases import (
    COMMAND_ALIASES,
    COMMAND_CATEGORIES,
    CATEGORY_DISPLAY,
    save_aliases
)
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

        # Две колонки с одинаковой структурой
        main_content.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        main_content.grid_rowconfigure(0, weight=1)

        # ==================== ЛЕВАЯ КОЛОНКА ====================
        left_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=16)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(left_frame, text="📁 КОМАНДЫ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"), 
                    text_color="#ff00c8").pack(pady=(22, 12), anchor="w", padx=22)

        scroll_left = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        scroll_left.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        for cat_key, display_name in CATEGORY_DISPLAY.items():
            commands = COMMAND_CATEGORIES.get(cat_key, [])
            count = len(commands)
            self.create_category_button(scroll_left, display_name, cat_key, count)

        # ==================== ПРАВАЯ КОЛОНКА ====================
        self.right_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=16)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.show_category("BASIC")

    def create_category_button(self, parent, display_name, cat_key, count):
        card = UniformCard(parent, text=display_name, count=count, height=56)
        
        card.bind("<Button-1>", lambda e, k=cat_key: self.show_category(k))
        card.bind("<Enter>", lambda e: card.configure(fg_color="#2a2a44"))
        card.bind("<Leave>", lambda e: card.configure(fg_color="#1a1a2e"))
        
        card.pack(pady=6, padx=12, fill="x")

    def show_category(self, category_key: str):
        self.current_category = category_key

        # Очищаем правую колонку
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Заголовок правой колонки (одинаковый стиль с левым)
        ctk.CTkLabel(self.right_frame, text=f"/commands/{category_key.lower()}", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"), 
                    text_color="#ff00c8").pack(pady=(22, 12), anchor="w", padx=22)

        scroll_right = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        scroll_right.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        # Список команд
        for cmd in sorted(COMMAND_CATEGORIES.get(category_key, [])):
            self.create_command_row(scroll_right, cmd)

    def create_command_row(self, parent, cmd_name):
        is_disabled = cmd_name in self.disabled_commands

        # Сильно уменьшили высоту правых строк
        card = UniformCard(parent, text=f"!{cmd_name}", height=48)   # ← было 52, теперь 48
        card.pack(pady=6, padx=12, fill="x")

        alias_str = self.get_short_aliases(cmd_name)

        if alias_str:
            alias_label = ctk.CTkLabel(card, text=alias_str,
                                     font=ctk.CTkFont(family="IBM Plex Mono", size=12),
                                     text_color="#88ddff")
            alias_label.place(relx=0.48, rely=0.5, anchor="w")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.place(relx=1.0, rely=0.5, anchor="e", x=-15)

        toggle_icon = "🔴" if is_disabled else "🟢"
        toggle_color = "#ff3366" if is_disabled else "#00ffaa"
        
        toggle_btn = ctk.CTkButton(btn_frame, text=toggle_icon, width=40, height=40,
                                  corner_radius=10, fg_color=toggle_color, 
                                  hover_color="#2a2a44", font=ctk.CTkFont(size=17),
                                  command=lambda c=cmd_name: self.toggle_command(c))
        toggle_btn.pack(side="left", padx=3)

        info_btn = ctk.CTkButton(btn_frame, text="ℹ", width=40, height=40,
                                corner_radius=10, fg_color="#6666ff", 
                                hover_color="#5555cc", font=ctk.CTkFont(size=16, weight="bold"),
                                command=lambda c=cmd_name: self.show_command_info(c))
        info_btn.pack(side="left", padx=3)

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

        # ==================== АЛИАСЫ ====================
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

        # Кнопка сохранения
        save_btn = ctk.CTkButton(alias_frame, text="💾 СОХРАНИТЬ АЛИАСЫ В ФАЙЛ", 
                                fg_color="#00ffaa", text_color="#000000", height=50,
                                font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                                command=self.save_current_aliases)
        save_btn.pack(pady=15, padx=20, fill="x")

        # ==================== ИНФОРМАЦИЯ ====================
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

    def save_current_aliases(self):
        if not hasattr(self, 'cmd_name_for_edit') or not hasattr(self, 'current_aliases'):
            self.ui.log_to_current_panel("Ошибка: нет данных для сохранения", "ERROR")
            return

        new_dict = COMMAND_ALIASES.copy()
        new_dict[self.cmd_name_for_edit] = self.current_aliases.copy()

        success, msg = save_aliases(new_dict)
        if success:
            self.ui.log_to_current_panel(msg, "SUCCESS")
            # ← Главное исправление: переоткрываем инфо команды, а не список
            self.show_command_info(self.cmd_name_for_edit)
        else:
            self.ui.log_to_current_panel(msg, "ERROR")

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