import customtkinter as ctk
import os


class AISettings(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="transparent")
        self.ui = ui
        self.setup()

    def setup(self):
        ctk.CTkLabel(self, text="🧠 AI Сервисы", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=24, weight="bold"),
                    text_color="#ff00c8").pack(pady=30)

        settings = [
            ("XAI_API_KEY", os.getenv("XAI_API_KEY", "")),
            ("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")),
        ]

        for name, value in settings:
            frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12, height=70)
            frame.pack(fill="x", padx=40, pady=10)
            frame.pack_propagate(False)

            ctk.CTkLabel(frame, text=name, width=200, anchor="w",
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=20)
            
            display = value[:12] + "..." + value[-6:] if value and len(value) > 18 else (value or "Не задан")
            ctk.CTkLabel(frame, text=display, text_color="#88ddff").pack(side="left")