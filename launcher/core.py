import subprocess
import threading
import sys
import os
import re

from launcher.config import BOT_FILE
import launcher.shared as shared


class BotCore:
    def __init__(self):
        self.bot_process = None
        self.is_running = False
        self.ui_callback = None

    def set_ui_callback(self, callback):
        self.ui_callback = callback

    def start_bot(self):
        if self.bot_process and self.bot_process.poll() is None:
            return False, "Бот уже запущен"

        try:
            self.bot_process = subprocess.Popen(
                [sys.executable, "-u", BOT_FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.getcwd(),
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            self.is_running = True
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
        try:
            for line in iter(self.bot_process.stdout.readline, ''):
                if not line:
                    continue
                line = line.strip()
                if not line:
                    continue

                prefix = "BOT"
                if any(x in line for x in ["✅", "успешно", "загружен", "готов"]):
                    prefix = "SUCCESS"
                elif any(x in line for x in ["❌", "ошибка", "failed", "ERROR"]):
                    prefix = "ERROR"
                elif any(x in line for x in ["🔄", "загрузка", "перезагру"]):
                    prefix = "SYSTEM"

                clean_line = re.sub(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\s*', '', line)

                if self.ui_callback:
                    self.ui_callback(clean_line, prefix)

        except Exception as e:
            if self.ui_callback:
                self.ui_callback(f"Ошибка чтения: {e}", "ERROR")

    def get_guilds(self):
        print("[DEBUG] get_guilds() был вызван")

        if not hasattr(shared, 'bot_instance') or shared.bot_instance is None:
            print("[DEBUG] shared.bot_instance = None")
            return None

        bot = shared.bot_instance
        print(f"[DEBUG] bot_instance существует, user = {getattr(bot, 'user', 'Ещё нет')}")

        is_ready = getattr(bot, 'is_ready', lambda: False)()
        guilds_count = len(getattr(bot, 'guilds', []))

        print(f"[DEBUG get_guilds] is_ready={is_ready} | guilds={guilds_count}")

        if not is_ready:
            return None

        return list(bot.guilds) if guilds_count > 0 else []

    def is_bot_running(self):
        return self.is_running and self.bot_process and self.bot_process.poll() is None