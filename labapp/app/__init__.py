import connexion
from flask_sqlalchemy import SQLAlchemy

def create_app(config_object):
	app = connexion.App(__name__, specification_dir='./')
	app.app.config.from_object(config_object)

	from .models import db

	db.init_app(app.app)

	app.add_api('api.yml')	

	return app.app