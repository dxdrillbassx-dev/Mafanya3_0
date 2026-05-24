import customtkinter as ctk
from utils.aliases import COMMAND_ALIASES


class CommandsPanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a12")
        self.ui = ui
        self.setup()

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=15, pady=15)

        # Левая панель — Структура команд
        left_frame = ctk.CTkFrame(main_content, fg_color="#111118", width=340, corner_radius=10)
        left_frame.pack(side="left", fill="y", padx=(0, 15))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="📁 Структура команд", 
                    font=ctk.CTkFont(size=15, weight="bold"), 
                    text_color="#00ffcc").pack(pady=(15, 10), anchor="w", padx=20)

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
            btn = ctk.CTkButton(left_frame, text=display_name, height=42, 
                              fg_color="#1a1a2e", hover_color="#2a2a44",
                              text_color="#cccccc", anchor="w", corner_radius=6,
                              font=ctk.CTkFont(family="Consolas", size=13))
            btn.configure(command=lambda k=cat_key: self.show_category(k))
            btn.pack(pady=4, padx=15, fill="x")

        # Правая панель — Команды
        self.right_frame = ctk.CTkFrame(main_content, fg_color="#0f0f1a", corner_radius=10)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.show_category("BASIC")

    def show_category(self, category_key: str):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header.pack(fill="x", pady=12, padx=20)

        ctk.CTkLabel(header, text=f"┌──(mafanya@bot)-[/commands/{category_key.lower()}]",
                    font=ctk.CTkFont(family="Consolas", size=14),
                    text_color="#00ff88").pack(anchor="w")

        ctk.CTkLabel(header, text="└─$ ls -la", 
                    font=ctk.CTkFont(family="Consolas", size=14),
                    text_color="#00ff88").pack(anchor="w", pady=2)

        scroll = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

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
            aliases = COMMAND_ALIASES.get(cmd, [])
            alias_str = f"[{', '.join(aliases)}]" if aliases else ""

            cmd_frame = ctk.CTkFrame(scroll, fg_color="#1a1a2e", corner_radius=6, height=52)
            cmd_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(cmd_frame, text=f"• !{cmd}", 
                        font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
                        text_color="#ffff00").pack(side="left", padx=20, pady=12)

            if alias_str:
                ctk.CTkLabel(cmd_frame, text=alias_str, 
                            font=ctk.CTkFont(family="Consolas", size=12),
                            text_color="#77ddff").pack(side="left", padx=10, pady=12)

    def log(self, message: str, prefix="INFO"):
        pass