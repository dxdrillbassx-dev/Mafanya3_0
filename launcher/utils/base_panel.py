# launcher/utils/base_panel.py
import customtkinter as ctk


class BasePanel(ctk.CTkFrame):
    """Базовый класс для всех панелей — обеспечивает единый стиль"""
    
    def __init__(self, parent, ui, title: str = "", icon: str = "📄"):
        super().__init__(parent, fg_color="#0a0a0f")
        self.ui = ui
        self.title = title
        self.icon = icon
        self.setup_base()

    def setup_base(self):
        """Создаёт общую структуру: заголовок + контент"""
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок панели
        header = ctk.CTkFrame(main_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(header, 
                    text=f"{self.icon} {self.title}", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=24, weight="bold"),
                    text_color="#ff00c8").pack(anchor="w")

        # Контейнер для основного контента
        self.content_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=16)
        self.content_frame.pack(fill="both", expand=True)

        # Вызываем метод, который будет переопределяться в дочерних классах
        self.build_content()

    def build_content(self):
        """Переопределяется в каждой панели"""
        pass