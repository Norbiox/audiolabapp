import os

from dotenv import load_dotenv
load_dotenv()


class Config:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('LABAPP_DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
