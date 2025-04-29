import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_FOLDER = os.getenv('MEDIA_FOLDER')
MEDIA_FOLDER_PATH = os.path.join(BASE_DIR, MEDIA_FOLDER)
