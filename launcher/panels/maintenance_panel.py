import customtkinter as ctk

class MaintenancePanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a0f")
        self.ui = ui
        self.setup()

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_content, text="🔧 ТЕХНИЧЕСКОЕ ОБСЛУЖИВАНИЕ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=22, weight="bold"), 
                    text_color="#ff00c8").pack(pady=(30, 40))

        center_frame = ctk.CTkFrame(main_content, fg_color="#111118", corner_radius=20)
        center_frame.pack(fill="both", expand=True, padx=60, pady=40)

        ctk.CTkLabel(center_frame, text="ПОЛНЫЙ ТЕХРЕЖИМ", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=28, weight="bold"), 
                    text_color="#ff3366").pack(pady=(60, 10))

        ctk.CTkLabel(center_frame, text="Отключает все команды кроме\nвладельца и основных", 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=14), 
                    text_color="#aaaaaa", justify="center").pack(pady=10)

        self.tech_button = ctk.CTkButton(center_frame, 
                                        text="🚨 ВКЛЮЧИТЬ ТЕХРЕЖИМ", 
                                        width=420, height=85, 
                                        corner_radius=16,
                                        font=ctk.CTkFont(family="IBM Plex Mono", size=18, weight="bold"),
                                        fg_color="#ff0066", 
                                        hover_color="#cc0044",
                                        command=self.ui.toggle_maintenance)
        self.tech_button.pack(pady=50)

        self.log("Панель техрежима загружена", "SYSTEM")

    def log(self, message: str, prefix="INFO"):
        try:
            if hasattr(self.ui.current_panel, 'log'):
                self.ui.current_panel.log(message, prefix)
        except:
            pass