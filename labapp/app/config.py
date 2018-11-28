import os

from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', default='172.17.0.3')
DB_PORT = os.getenv('DB_PORT', default='3306')

DEBUG = True
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/mysql".format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
)
