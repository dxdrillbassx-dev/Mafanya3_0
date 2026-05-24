# launcher/core.py
import subprocess
import threading
import sys
import os

# Правильный импорт
from launcher.config import BOT_FILE

class BotCore:
    def __init__(self):
        self.bot_process = None
        self.is_running = False

    def start_bot(self):
        if self.bot_process and self.bot_process.poll() is None:
            return False, "Бот уже запущен"

        try:
            self.bot_process = subprocess.Popen(
                [sys.executable, BOT_FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.getcwd()
            )
            self.is_running = True
            
            # Запускаем чтение вывода в отдельном потоке
            threading.Thread(target=self._read_output, daemon=True).start()
            return True, "Бот успешно запущен"
            
        except Exception as e:
            return False, f"Ошибка запуска: {e}"

    def stop_bot(self):
        if self.bot_process and self.bot_process.poll() is None:
            self.bot_process.terminate()
            try:
                self.bot_process.wait(timeout=5)
            except:
                self.bot_process.kill()
            self.is_running = False
            return True, "Бот остановлен"
        return False, "Бот не был запущен"

    def _read_output(self):
        """Читает вывод бота в реальном времени"""
        for line in self.bot_process.stdout:
            if line.strip():
                # Здесь можно добавить callback для логов, но пока просто пропускаем
                pass