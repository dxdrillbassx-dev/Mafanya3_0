# launcher/utils/uniform_card.py
import customtkinter as ctk

class UniformCard(ctk.CTkFrame):
    def __init__(self, parent, text: str, count: str = None, icon: str = None, height: int = 56):
        super().__init__(parent, fg_color="#1a1a2e", corner_radius=12, height=height)
        self.pack_propagate(False)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=10)

        if icon:
            ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=16)).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(inner, text=text, 
                    font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                    text_color="#e0f8ff", anchor="w").pack(side="left", fill="x", expand=True)

        if count is not None:
            ctk.CTkLabel(inner, text=str(count), 
                        font=ctk.CTkFont(family="IBM Plex Mono", size=14, weight="bold"),
                        text_color="#ff00c8").pack(side="right")