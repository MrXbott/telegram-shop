import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем PYTHONPATH из .env в sys.path (если задан)
project_root = os.getenv('PYTHONPATH', '.')
abs_path = os.path.abspath(project_root)
if abs_path not in sys.path:
    sys.path.insert(0, abs_path)

# Запускаем Flask-приложение
from admin.main import app

if __name__ == '__main__':
    app.run(debug=True)
