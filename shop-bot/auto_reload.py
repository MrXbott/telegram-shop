import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = self.run_script()

    def run_script(self):
        print(f"🚀 Запуск: python {self.script_name}")
        return subprocess.Popen([sys.executable, self.script_name])

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print(f"🔄 Изменение обнаружено: {event.src_path}, перезапускаем...")
            self.process.terminate()
            self.process.wait()
            self.process = self.run_script()


if __name__ == "__main__":
    script_to_watch = "bot.py"  # замените на свой основной файл
    event_handler = RestartOnChangeHandler(script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.process.terminate()

    observer.join()
