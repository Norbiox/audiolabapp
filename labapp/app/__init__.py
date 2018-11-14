import connexion

def create_app(config_object):
	app = connexion.App(__name__, specification_dir='./api/')
	app.add_api('lab.yml')
	#app.app.config.from_object(config_object)
	return app.app