import os

from dotenv import load_dotenv
from pathlib import Path
load_dotenv()


class Config:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY',
                           default='uber-secretly-keeped-in-memory-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_DEFAULT_DEST = \
        Path(os.getenv('MEDIA_DIR', default=os.getcwd())) / "media"
    UPLOADS_DEFAULT_DEST.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    UPLOADS_DEFAULT_DEST = Path("/tmp/media")
    UPLOADS_DEFAULT_DEST.mkdir(exist_ok=True)
