import customtkinter as ctk
import os


class ServicesSettings(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="transparent")
        self.ui = ui
        self.setup()

    def setup(self):
        ctk.CTkLabel(self, text="🌍 Внешние Сервисы", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=24, weight="bold"),
                    text_color="#ff00c8").pack(pady=30)

        settings = [
            ("PINTEREST_EMAIL", os.getenv("PINTEREST_EMAIL", "Не задан")),
            ("VK_TOKEN", os.getenv("VK_TOKEN", "")),
            ("FORZA_UDP_PORT", os.getenv("FORZA_UDP_PORT", "8001")),
        ]

        for name, value in settings:
            frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12, height=60)
            frame.pack(fill="x", padx=40, pady=8)
            frame.pack_propagate(False)

            ctk.CTkLabel(frame, text=name, width=200, anchor="w",
                        font=ctk.CTkFont(weight="bold")).pack(side="left", padx=20)
            ctk.CTkLabel(frame, text=value[:30] + "..." if len(str(value)) > 30 else value,
                        text_color="#88ddff").pack(side="left")