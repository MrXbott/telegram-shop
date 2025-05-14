import sys
import os
from config import PYTHONPATH

abs_path = os.path.abspath(PYTHONPATH)
if abs_path not in sys.path:
    sys.path.insert(0, abs_path)

from admin import create_app

app = create_app('dev')

if __name__ == '__main__':
    app.run(debug=True)
