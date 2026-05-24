# launcher/panels/maintenance_panel.py
import customtkinter as ctk

class MaintenancePanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a12")
        self.ui = ui
        self.setup()

    def setup(self):
        ctk.CTkLabel(self, text="🔧 ТЕХНИЧЕСКИЕ РАБОТЫ", 
                    font=ctk.CTkFont(size=28, weight="bold"), 
                    text_color="#ff00ff").pack(pady=40)

        ctk.CTkLabel(self, text="Управление режимом техобслуживания", 
                    font=ctk.CTkFont(size=16), 
                    text_color="#aaaaaa").pack(pady=10)

        self.tech_button = ctk.CTkButton(self, text="🚨 ВКЛЮЧИТЬ ПОЛНЫЙ ТЕХРЕЖИМ", 
                                        width=400, height=70, corner_radius=12,
                                        font=ctk.CTkFont(size=18, weight="bold"),
                                        fg_color="#ff0066", hover_color="#cc0044",
                                        command=self.ui.toggle_maintenance)
        self.tech_button.pack(pady=40)