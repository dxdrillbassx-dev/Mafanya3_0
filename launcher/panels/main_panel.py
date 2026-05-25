import customtkinter as ctk
import time
import pyperclip


class MainPanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a0f")
        self.ui = ui
        self.setup()

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # ====================== ЛЕВАЯ КОЛОНКА — УПРАВЛЕНИЕ ======================
        control_frame = ctk.CTkFrame(main_content, fg_color="#111118", width=390, corner_radius=16)
        control_frame.pack(side="left", fill="y", padx=(0, 20))
        control_frame.pack_propagate(False)

        ctk.CTkLabel(control_frame, text="📊 ПАНЕЛЬ УПРАВЛЕНИЯ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"), 
                    text_color="#ff00c8").pack(pady=(30, 20), anchor="w", padx=25)

        # Статус
        self.status_frame = ctk.CTkFrame(control_frame, fg_color="#1a1a2e", height=140, corner_radius=16)
        self.status_frame.pack(fill="x", padx=25, pady=15)
        self.status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(self.status_frame, text="OFFLINE", 
                                        font=ctk.CTkFont(family="IBM Plex Mono", size=42, weight="bold"),
                                        text_color="#ff3366")
        self.status_label.pack(expand=True)

        # Кнопки
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.pack(pady=20, padx=25, fill="x")

        self.start_btn = ctk.CTkButton(btn_frame, 
                                       text="▶ ЗАПУСТИТЬ БОТА", 
                                       height=65, 
                                       corner_radius=16,
                                       font=ctk.CTkFont(family="IBM Plex Mono", size=17, weight="bold"),
                                       fg_color="#00ffaa", 
                                       text_color="#000000",
                                       hover_color="#00cc88",
                                       command=self.ui.toggle_bot)
        self.start_btn.pack(fill="x", pady=6)

        self.kill_btn = ctk.CTkButton(btn_frame, 
                                      text="⛔ ОСТАНОВИТЬ БОТА", 
                                      height=50,
                                      corner_radius=12,
                                      font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                                      fg_color="#ff5500",
                                      command=self.ui.toggle_bot)
        self.kill_btn.pack(fill="x", pady=6)

        # === НОВАЯ КНОПКА ===
        self.nuke_btn = ctk.CTkButton(btn_frame, 
                                      text="☢ УБИТЬ ВСЕ ПРОЦЕССЫ МАФАНИ", 
                                      height=55,
                                      corner_radius=12,
                                      font=ctk.CTkFont(family="IBM Plex Mono", size=15, weight="bold"),
                                      fg_color="#ff0000", 
                                      hover_color="#aa0000",
                                      text_color="white",
                                      command=self.ui.nuke_all_processes)
        self.nuke_btn.pack(fill="x", pady=8)

        # ====================== ПРАВАЯ КОЛОНКА — ЛОГИ ======================
        log_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=16)
        log_frame.pack(side="right", fill="both", expand=True)

        header = ctk.CTkFrame(log_frame, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(header, text="📜 СИСТЕМНЫЕ ЛОГИ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=17, weight="bold"), 
                    text_color="#ff00c8").pack(side="left")

        copy_btn = ctk.CTkButton(header, text="📋 Копировать", width=130, height=32,
                                fg_color="#ff00c8", hover_color="#d100a8",
                                command=self.copy_console)
        copy_btn.pack(side="right")

        self.console = ctk.CTkTextbox(log_frame, 
                                     font=ctk.CTkFont(family="IBM Plex Mono", size=13),
                                     fg_color="#050508", 
                                     text_color="#a0f0ff", 
                                     scrollbar_button_color="#ff00c8",
                                     wrap="word")
        self.console.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.log("Главная панель загружена", "SYSTEM")

    def log(self, message: str, prefix="INFO"):
        ts = time.strftime("%H:%M:%S")
        self.console.insert("end", f"[{ts}] [{prefix}] {message}\n")
        self.console.see("end")

    def copy_console(self):
        try:
            text = self.console.get("1.0", "end").strip()
            pyperclip.copy(text)
            self.log("✅ Логи скопированы в буфер", "SUCCESS")
        except:
            self.log("❌ Не удалось скопировать", "ERROR")