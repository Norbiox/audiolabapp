import jwt
from functools import wraps

import flask
from sqlalchemy.orm import exc

from .helpers import get_object
from .models import Recorder


def recorder_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            token = flask.request.headers.get('recorder_key')
            assert token is not None
            if isinstance(token, str):
                token = token.encode("utf-8")
            payload = jwt.decode(token, flask.current_app.config['SECRET_KEY'],
                                 algorithms=['HS256'])
            uid = payload.pop('uid')
            recorder = get_object(Recorder, uid)
            setattr(flask.g, 'recorder', recorder)
            return func(*args, **kwargs)
        except (jwt.exceptions.InvalidSignatureError, KeyError) as ex:
            flask.abort(401)
        except (exc.NoResultFound, AssertionError) as ex:
            flask.abort(401)
    return inner
