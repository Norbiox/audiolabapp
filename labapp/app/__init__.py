import datetime
import connexion
import json
from decimal import Decimal

from flask_migrate import Migrate


class FlaskJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat('T')

        if isinstance(o, datetime.date):
            return o.isoformat()

        if isinstance(o, Decimal):
            return float(o)
        return json.JSONEncoder.default(self, o)


def create_app(config_object):
    app = connexion.App(__name__, specification_dir='./')
    app.app.config.from_object(config_object)

    from .models import db

    db.init_app(app.app)
    Migrate(app.app, db)

    app.add_api('labapp_api.yml')
    app.app.json_encoder = FlaskJSONEncoder

    return app.app
