import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    APP_ADMIN = os.environ.get('APP_ADMIN')
    MEDIA_FOLDER = os.getenv('MEDIA_FOLDER')
    MEDIA_FOLDER_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', MEDIA_FOLDER)


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass


config = {
    'dev': DevelopmentConfig,
    'testing': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}