import customtkinter as ctk


class BasicSettings(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="transparent")
        self.ui = ui
        self.setup()

    def setup(self):
        ctk.CTkLabel(self, text="🌐 Основные настройки", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=24, weight="bold"),
                    text_color="#ff00c8").pack(pady=30)

        ctk.CTkLabel(self, text="Раздел находится в разработке", 
                    font=ctk.CTkFont(size=16), text_color="#888888").pack(pady=20)