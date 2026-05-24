import customtkinter as ctk

class MaintenancePanel(ctk.CTkFrame):
    def __init__(self, parent, ui):
        super().__init__(parent, fg_color="#0a0a12")
        self.ui = ui
        self.setup()

    def setup(self):
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=15, pady=15)

        # Левая колонка
        left_frame = ctk.CTkFrame(main_content, fg_color="#111118", width=280, corner_radius=10)
        left_frame.pack(side="left", fill="y", padx=(0, 15))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="🔧 ТЕХРЕЖИМ", 
                    font=ctk.CTkFont(size=15, weight="bold"), 
                    text_color="#00ffcc").pack(pady=(20, 12), anchor="w", padx=20)

        # Центральная + правая часть
        right_area = ctk.CTkFrame(main_content, fg_color="transparent")
        right_area.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_area, text="🔧 ТЕХНИЧЕСКИЕ РАБОТЫ", 
                    font=ctk.CTkFont(size=32, weight="bold"), 
                    text_color="#ff00ff").pack(pady=40)

        ctk.CTkLabel(right_area, text="Управление режимом техобслуживания", 
                    font=ctk.CTkFont(size=16), 
                    text_color="#aaaaaa").pack(pady=10)

        self.tech_button = ctk.CTkButton(right_area, text="🚨 ВКЛЮЧИТЬ ПОЛНЫЙ ТЕХРЕЖИМ", 
                                        width=420, height=80, corner_radius=12,
                                        font=ctk.CTkFont(size=18, weight="bold"),
                                        fg_color="#ff0066", hover_color="#cc0044",
                                        command=self.ui.toggle_maintenance)
        self.tech_button.pack(pady=60)

        # Можно добавить сюда дополнительные настройки техрежима позже