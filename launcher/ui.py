# launcher/ui.py
import tkinter as tk
from tkinter import scrolledtext, ttk
import time
import os
import json

from launcher.config import TITLE, GEOMETRY, CONSOLE_FONT
from launcher.core import BotCore


class RetroLauncherUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(TITLE)
        self.root.geometry(GEOMETRY)
        self.root.configure(bg="#0f0f1a")
        self.root.resizable(False, False)

        self.core = BotCore()
        self.full_maintenance_mode = False

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Accent.TButton", background="#ff00ff", foreground="white")

    def setup_ui(self):
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg="#0f0f1a")
        main_frame.pack(fill="both", expand=True)

        # === Сайдбар ===
        sidebar = tk.Frame(main_frame, bg="#151521", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="MAFANYA 3.0", font=("Segoe UI", 20, "bold"), 
                fg="#ff00ff", bg="#151521").pack(pady=20)

        # Навигация
        nav_items = [
            ("🌐 Главная", self.show_main),
            ("🔧 Техрежим", self.show_maintenance),
            ("📊 Статистика", lambda: self.log("Статистика пока в разработке")),
            ("🔄 Управление", self.show_main),
            ("⚙️ Настройки", lambda: self.log("Настройки в разработке")),
        ]

        for text, cmd in nav_items:
            btn = tk.Button(sidebar, text=text, bg="#1f1f2e", fg="#cccccc", 
                          activebackground="#ff00ff", activeforeground="white",
                          font=("Segoe UI", 11), relief="flat", anchor="w", padx=20)
            btn.config(command=cmd)
            btn.pack(fill="x", pady=2, padx=10)

        # === Основная область ===
        self.content_frame = tk.Frame(main_frame, bg="#0f0f1a")
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.show_main()  # Показываем главную по умолчанию

    def show_main(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header
        header = tk.Label(self.content_frame, text="ПАНЕЛЬ УПРАВЛЕНИЯ", 
                         font=("Segoe UI", 24, "bold"), fg="#ff00ff", bg="#0f0f1a")
        header.pack(pady=20)

        # Статус бота
        status_frame = tk.Frame(self.content_frame, bg="#1a1a2e", height=120)
        status_frame.pack(fill="x", padx=30, pady=10)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text="OFFLINE", 
                                    font=("Segoe UI", 28, "bold"), fg="#ff3333", bg="#1a1a2e")
        self.status_label.pack(pady=30)

        # Кнопки управления
        btn_frame = tk.Frame(self.content_frame, bg="#0f0f1a")
        btn_frame.pack(pady=20)

        self.start_btn = tk.Button(btn_frame, text="▶ ЗАПУСТИТЬ БОТА", width=25, height=3,
                                  font=("Segoe UI", 14, "bold"), bg="#00ff88", fg="black",
                                  command=self.toggle_bot)
        self.start_btn.grid(row=0, column=0, padx=15)

        self.tech_btn = tk.Button(btn_frame, text="🚨 ТЕХРЕЖИМ OFF", width=25, height=3,
                                 font=("Segoe UI", 14, "bold"), bg="#444466", fg="#ffff00",
                                 command=self.toggle_maintenance)
        self.tech_btn.grid(row=0, column=1, padx=15)

        # Логи
        log_frame = tk.LabelFrame(self.content_frame, text=" ЛОГИ ", fg="#8888ff", bg="#0f0f1a")
        log_frame.pack(fill="both", expand=True, padx=30, pady=15)

        self.console = scrolledtext.ScrolledText(log_frame, font=CONSOLE_FONT,
                                                 bg="#0a0a12", fg="#00ffcc", height=18)
        self.console.pack(fill="both", expand=True, padx=10, pady=10)

        self.log("MAFANYA 3.0 — Современная панель управления загружена", "SYSTEM")

    def show_maintenance(self):
        # Можно сделать отдельную вкладку с подробным техрежимом позже
        self.log("Открыта панель техрежима", "INFO")

    def log(self, message: str, prefix="INFO"):
        ts = time.strftime("%H:%M:%S")
        color = "#00ffcc"
        self.console.insert(tk.END, f"[{ts}] [{prefix}] {message}\n")
        self.console.see(tk.END)

    def toggle_bot(self):
        if not self.core.is_running:
            success, msg = self.core.start_bot()
            if success:
                self.start_btn.config(text="■ ОСТАНОВИТЬ БОТА", bg="#ff3366", fg="white")
                self.status_label.config(text="ONLINE", fg="#00ff88")
            self.log(msg, "SUCCESS" if success else "ERROR")
        else:
            success, msg = self.core.stop_bot()
            if success:
                self.start_btn.config(text="▶ ЗАПУСТИТЬ БОТА", bg="#00ff88", fg="black")
                self.status_label.config(text="OFFLINE", fg="#ff3333")
            self.log(msg, "SYSTEM")

    def toggle_maintenance(self):
        self.full_maintenance_mode = not self.full_maintenance_mode

        if self.full_maintenance_mode:
            self.tech_btn.config(text="🚨 ТЕХРЕЖИМ ON", bg="#ff0066", fg="white")
            self.log("ПОЛНЫЙ ТЕХРЕЖИМ ВКЛЮЧЁН", "CRITICAL")
        else:
            self.tech_btn.config(text="🚨 ТЕХРЕЖИМ OFF", bg="#444466", fg="#ffff00")
            self.log("ТЕХРЕЖИМ ВЫКЛЮЧЕН", "SYSTEM")

    def run(self):
        self.root.mainloop()