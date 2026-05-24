import customtkinter as ctk

class ChatsPanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a0f")
        self.ui = ui
        self.current_mode = "guilds"
        self.setup()

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Левая колонка
        left_frame = ctk.CTkFrame(main_content, fg_color="#111118", width=340, corner_radius=16)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="💬 ЧАТЫ И СООБЩЕНИЯ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"), 
                    text_color="#ff00c8").pack(pady=(25, 15), anchor="w", padx=25)

        guild_btn = ctk.CTkButton(left_frame, text="🌐 Серверы", height=52,
                                 fg_color="#1a1a2e", hover_color="#ff00c8",
                                 text_color="#e0f8ff", anchor="w", corner_radius=12,
                                 font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"))
        guild_btn.configure(command=lambda: self.switch_mode("guilds"))
        guild_btn.pack(pady=8, padx=20, fill="x")

        dm_btn = ctk.CTkButton(left_frame, text="👤 Личные сообщения", height=52,
                              fg_color="#1a1a2e", hover_color="#ff00c8",
                              text_color="#e0f8ff", anchor="w", corner_radius=12,
                              font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"))
        dm_btn.configure(command=lambda: self.switch_mode("dms"))
        dm_btn.pack(pady=8, padx=20, fill="x")

        # Правая колонка
        self.right_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=16)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.switch_mode("guilds")

    def switch_mode(self, mode: str):
        self.current_mode = mode
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        if mode == "guilds":
            self.show_guilds_view()
        else:
            self.show_dms_view()

    def show_guilds_view(self):
        header = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header.pack(fill="x", pady=15, padx=25)

        ctk.CTkLabel(header, text="🌐 СЕРВЕРЫ БОТА",
                    font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"),
                    text_color="#ff00c8").pack(anchor="w", side="left")

        refresh_btn = ctk.CTkButton(header, text="⟳ ОБНОВИТЬ", width=160, height=40,
                                   fg_color="#ff00c8", hover_color="#d100a8",
                                   font=ctk.CTkFont(family="IBM Plex Mono", size=13, weight="bold"),
                                   command=self.load_guilds)
        refresh_btn.pack(side="right")

        self.guilds_scroll = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        self.guilds_scroll.pack(fill="both", expand=True, padx=25, pady=10)

        self.load_guilds()

    def load_guilds(self):
        for widget in self.guilds_scroll.winfo_children():
            widget.destroy()

        if not self.ui.core.is_bot_running():
            self.show_status("❌ Бот не запущен", "Запустите бота сначала", "#ff3366")
            return

        loading = ctk.CTkLabel(self.guilds_scroll, 
                              text="⏳ Ожидаем подключение к Discord...",
                              font=ctk.CTkFont(family="IBM Plex Mono", size=14), 
                              text_color="#888888")
        loading.pack(pady=80)

        self.guilds_scroll.after(2000, self._fetch_guilds)

    def _fetch_guilds(self):
        for widget in self.guilds_scroll.winfo_children():
            widget.destroy()

        guilds = self.ui.core.get_guilds()
        
        if guilds is None:
            self.show_status(
                "⏳ Бот ещё не готов",
                "Ждём ready event...\nАвтообновление через 4 секунды.",
                "#ffaa44"
            )
            self.guilds_scroll.after(4000, self._fetch_guilds)
            return

        guild_count = len(guilds) if guilds else 0

        if guild_count > 0:
            count_label = ctk.CTkLabel(self.guilds_scroll, 
                                      text=f"🌐 Найдено серверов: {guild_count}",
                                      font=ctk.CTkFont(family="IBM Plex Mono", size=17, weight="bold"),
                                      text_color="#00ffaa")
            count_label.pack(pady=(10, 20))

            for guild in sorted(guilds, key=lambda g: g.name.lower()):
                frame = ctk.CTkFrame(self.guilds_scroll, fg_color="#1a1a2e", corner_radius=12)
                frame.pack(fill="x", pady=8, padx=5)

                ctk.CTkLabel(frame, text=f"🌐 {guild.name}", 
                            font=ctk.CTkFont(family="IBM Plex Mono", size=15, weight="bold"),
                            text_color="#ffffff").pack(anchor="w", padx=20, pady=(14, 2))
                ctk.CTkLabel(frame, text=f"ID: {guild.id} • {guild.member_count:,} участников", 
                            font=ctk.CTkFont(family="IBM Plex Mono", size=12),
                            text_color="#888888").pack(anchor="w", padx=20, pady=(0, 14))
        else:
            self.show_status("🤔 Серверы не найдены", "Бот готов, но список пуст.", "#ffaa44")

    def show_status(self, title: str, description: str, color: str):
        frame = ctk.CTkFrame(self.guilds_scroll, fg_color="#1a1a2e", corner_radius=16)
        frame.pack(fill="both", expand=True, padx=60, pady=100)

        ctk.CTkLabel(frame, text=title, 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"), 
                    text_color=color).pack(pady=(50, 15))

        ctk.CTkLabel(frame, text=description, 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=13), 
                    text_color="#aaaaaa", justify="center").pack(pady=10, padx=40)

        ctk.CTkButton(frame, text="⟳ Попробовать снова", 
                     fg_color="#ff00c8", height=45,
                     font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                     command=self.load_guilds).pack(pady=30)

    def show_dms_view(self):
        frame = ctk.CTkFrame(self.right_frame, fg_color="#1a1a2e", corner_radius=16)
        frame.pack(fill="both", expand=True, padx=80, pady=120)

        ctk.CTkLabel(frame, text="👤 ЛИЧНЫЕ СООБЩЕНИЯ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=20, weight="bold"), 
                    text_color="#666666").pack(pady=30)
        ctk.CTkLabel(frame, text="(в разработке)", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=14), 
                    text_color="#555555").pack()

    def log(self, message: str, prefix="INFO"):
        pass