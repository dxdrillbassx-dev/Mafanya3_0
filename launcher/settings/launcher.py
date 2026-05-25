import customtkinter as ctk


class LauncherSettings(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="transparent")
        self.ui = ui
        self.setup()

    def setup(self):
        ctk.CTkLabel(self, text="🎨 Настройки Лаунчера", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=24, weight="bold"),
                    text_color="#ff00c8").pack(pady=30)

        ctk.CTkLabel(self, text="Тема, цвета, шрифты и поведение лаунчера", 
                    font=ctk.CTkFont(size=16), text_color="#aaaaaa").pack(pady=10)

        # Заглушка
        ctk.CTkLabel(self, text="Раздел в разработке", 
                    font=ctk.CTkFont(size=18), text_color="#555555").pack(pady=80)