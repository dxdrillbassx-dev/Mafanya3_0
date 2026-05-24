import customtkinter as ctk
import time


class MainPanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a12")
        self.ui = ui
        self.setup()

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=15, pady=15)

        # ====================== ЛЕВАЯ КОЛОНКА — УПРАВЛЕНИЕ ======================
        control_frame = ctk.CTkFrame(main_content, fg_color="#111118", width=340, corner_radius=12)
        control_frame.pack(side="left", fill="y", padx=(0, 15))
        control_frame.pack_propagate(False)

        ctk.CTkLabel(control_frame, text="📊 ПАНЕЛЬ УПРАВЛЕНИЯ", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color="#00ffcc").pack(pady=(30, 20), anchor="w", padx=25)

        # Большой статус
        self.status_frame = ctk.CTkFrame(control_frame, fg_color="#1a1a2e", height=160, corner_radius=12)
        self.status_frame.pack(fill="x", padx=25, pady=15)
        self.status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(self.status_frame, text="OFFLINE", 
                                        font=ctk.CTkFont(size=42, weight="bold"),
                                        text_color="#ff4444")
        self.status_label.pack(expand=True)

        # Большая кнопка
        self.start_btn = ctk.CTkButton(control_frame, 
                                       text="▶ ЗАПУСТИТЬ БОТА", 
                                       width=290, height=70, 
                                       corner_radius=12,
                                       font=ctk.CTkFont(size=18, weight="bold"),
                                       fg_color="#00ff88", 
                                       text_color="black",
                                       hover_color="#00cc6a",
                                       command=self.ui.toggle_bot)
        self.start_btn.pack(pady=30)

        # ====================== ПРАВАЯ КОЛОНКА — ЛОГИ ======================
        log_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=12)
        log_frame.pack(side="right", fill="both", expand=True)

        log_label = ctk.CTkLabel(log_frame, text="📜 СИСТЕМНЫЕ ЛОГИ", 
                                font=ctk.CTkFont(size=16, weight="bold"), 
                                text_color="#7777ff")
        log_label.pack(pady=(20, 8), anchor="w", padx=25)

        self.console = ctk.CTkTextbox(log_frame, 
                                     font=ctk.CTkFont(family="Consolas", size=12),
                                     fg_color="#050508", 
                                     text_color="#00ffcc", 
                                     scrollbar_button_color="#ff00ff")
        self.console.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        self.log("Главная панель загружена", "SYSTEM")

    def log(self, message: str, prefix="INFO"):
        ts = time.strftime("%H:%M:%S")
        self.console.insert("end", f"[{ts}] [{prefix}] {message}\n")
        self.console.see("end")