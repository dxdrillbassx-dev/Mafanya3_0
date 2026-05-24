# launcher/panels/main_panel.py
import customtkinter as ctk
import time


class MainPanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a12")
        self.ui = ui
        self.setup()

    def setup(self):
        # Заголовок
        title = ctk.CTkLabel(self, text="ПАНЕЛЬ УПРАВЛЕНИЯ", 
                            font=ctk.CTkFont(size=32, weight="bold"), 
                            text_color="#ff00ff")
        title.pack(pady=25)

        # Статус блок
        status_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", height=160, corner_radius=12)
        status_frame.pack(fill="x", padx=40, pady=20)
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(status_frame, text="OFFLINE", 
                                        font=ctk.CTkFont(size=42, weight="bold"),
                                        text_color="#ff4444")
        self.status_label.pack(expand=True, pady=40)

        # Кнопки
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.start_btn = ctk.CTkButton(btn_frame, text="▶ ЗАПУСТИТЬ БОТА", 
                                      width=280, height=60, corner_radius=12,
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      fg_color="#00ff88", text_color="black",
                                      hover_color="#00cc6a",
                                      command=self.ui.toggle_bot)
        self.start_btn.pack(side="left", padx=20)

        self.tech_btn = ctk.CTkButton(btn_frame, text="🚨 ТЕХРЕЖИМ OFF", 
                                     width=280, height=60, corner_radius=12,
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     fg_color="#444466", text_color="#ffff00",
                                     hover_color="#666688",
                                     command=self.ui.toggle_maintenance)
        self.tech_btn.pack(side="left", padx=20)

        # Логи
        log_frame = ctk.CTkFrame(self, fg_color="#111118")
        log_frame.pack(fill="both", expand=True, padx=40, pady=20)

        log_label = ctk.CTkLabel(log_frame, text="ЛОГИ", 
                                font=ctk.CTkFont(size=16, weight="bold"), 
                                text_color="#7777ff")
        log_label.pack(pady=(15, 5))

        self.console = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=11),
                                     fg_color="#050508", text_color="#00ffcc", 
                                     scrollbar_button_color="#ff00ff")
        self.console.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.log("Главная панель загружена", "SYSTEM")

    def log(self, message: str, prefix="INFO"):
        ts = time.strftime("%H:%M:%S")
        self.console.insert("end", f"[{ts}] [{prefix}] {message}\n")
        self.console.see("end")