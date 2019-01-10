import os
from app import create_app

config = os.getenv('FLASK_CONFIG') or 'app.config.ProductionConfig'
app = create_app(config)

if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.info')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run()
