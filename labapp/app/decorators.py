import jwt
from functools import wraps

import flask
from .helpers import get_object_or_404
from .models import Recorder


def recorder_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        token = flask.request.headers.get('recorder_key')
        try:
            payload = jwt.decode(token, flask.current_app.config['SECRET_KEY'],
                                 algorithms=['HS256'])
            uid = payload.pop('uid')
            recorder = get_object_or_404(Recorder, uid)
            setattr(flask.g, 'recorder', recorder)
            return func(*args, **kwargs)
        except jwt.exceptions.InvalidSignatureError as ex:
            flask.abort(400, str(ex))
        except KeyError as ex:
            flask.abort(400, str(ex))
