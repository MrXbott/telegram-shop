import subprocess
import sys
import os

app_path = os.path.join(os.path.dirname(__file__), 'admin', 'app.py')
subprocess.run([sys.executable, app_path])