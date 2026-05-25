import subprocess
import threading
import sys
import os
import re
import time

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
                self.bot_process.wait(timeout=4)
            except:
                self.bot_process.kill()
            self.is_running = False
            self.bot_process = None
            return True, "Бот остановлен"
        return False, "Бот не был запущен"

    def force_kill(self):
        if self.bot_process and self.bot_process.poll() is None:
            try:
                self.bot_process.kill()
                self.bot_process.wait(timeout=3)
            except:
                pass
            self.is_running = False
            self.bot_process = None
            return True, "✅ Текущий процесс убит"
        return False, "Бот не запущен"

    def kill_all_python_processes(self):
        """МАКСИМАЛЬНО АГРЕССИВНАЯ ОЧИСТКА"""
        killed = 0
        self.log_to_ui("☢ Запущена ядерная очистка всех процессов Mafanya...", "CRITICAL")

        try:
            if os.name == 'nt':  # Windows
                # 1. Убиваем по имени окна и названию файла
                subprocess.run('taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *bot*"', 
                             shell=True, capture_output=True)

                subprocess.run('taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *mafanya*"', 
                             shell=True, capture_output=True)

                # 2. Убиваем все python.exe, в командной строке которых есть bot.py или launcher
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV', '/NH'],
                    capture_output=True, text=True, encoding='cp866'
                )

                for line in result.stdout.splitlines():
                    if any(x in line for x in [BOT_FILE, 'bot.py', 'mafanya', 'launcher']):
                        try:
                            pid = int(line.split(',')[1].strip('"'))
                            subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                         capture_output=True, timeout=5)
                            killed += 1
                            self.log_to_ui(f"Убит процесс PID: {pid}", "CRITICAL")
                        except:
                            pass

                # 3. Самая жёсткая очистка — убиваем все python.exe (с предупреждением)
                if killed == 0:
                    self.log_to_ui("Предупреждение: убиваем ВСЕ python процессы...", "WARNING")
                    subprocess.run('taskkill /F /IM python.exe', shell=True, capture_output=True)
                    killed += 3  # примерное значение

            else:  # Linux/macOS
                result = subprocess.run(['ps', '-ef'], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if 'python' in line and any(x in line for x in ['bot.py', 'mafanya', 'launcher']):
                        try:
                            pid = int(line.split()[1])
                            subprocess.run(['kill', '-9', str(pid)], capture_output=True)
                            killed += 1
                        except:
                            pass

            time.sleep(1.5)

            if killed > 0:
                msg = f"✅ Ядерная очистка завершена. Убито ~{killed} процессов."
                self.log_to_ui(msg, "CRITICAL")
                return True, msg
            else:
                return True, "ℹ️ Процессы не найдены (бот может быть уже мёртв)"

        except Exception as e:
            error = f"Ошибка ядерной очистки: {e}"
            self.log_to_ui(error, "ERROR")
            return False, error

    def _read_output(self):
        try:
            for line in iter(self.bot_process.stdout.readline, ''):
                if not line:
                    continue
                line = line.strip()
                if not line:
                    continue

                prefix = "BOT"
                lower = line.lower()
                if any(x in lower for x in ["✅", "успешно", "загружен", "готов"]):
                    prefix = "SUCCESS"
                elif any(x in lower for x in ["❌", "ошибка", "failed", "error"]):
                    prefix = "ERROR"
                elif any(x in lower for x in ["🔄", "загрузка", "перезагру"]):
                    prefix = "SYSTEM"

                clean_line = re.sub(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\s*', '', line)

                if self.ui_callback:
                    self.ui_callback(clean_line, prefix)

        except Exception as e:
            if self.ui_callback:
                self.ui_callback(f"Ошибка чтения: {e}", "ERROR")

    def log_to_ui(self, message: str, prefix="INFO"):
        if self.ui_callback:
            self.ui_callback(message, prefix)

    def is_bot_running(self):
        return self.is_running and self.bot_process and self.bot_process.poll() is None

    def get_guilds(self):
        if not hasattr(shared, 'bot_instance') or shared.bot_instance is None:
            return None

        bot = shared.bot_instance
        is_ready = getattr(bot, 'is_ready', lambda: False)()
        if not is_ready:
            return None
        return list(bot.guilds) if len(getattr(bot, 'guilds', [])) > 0 else []