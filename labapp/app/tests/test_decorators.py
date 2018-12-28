import flask
import pytest

from werkzeug.datastructures import Headers

from app.tests.fact import models
from app.helpers import encode_recorder_key


@pytest.mark.usefixtures('database')
def test_recorder_required(app, client):
    from app.decorators import recorder_required

    @recorder_required
    def test_endpoint():
        return 'Success'

    print(test_endpoint)

    # correct recorder key
    recorder = models.RecorderFactory.create(uid="Recorder12")
    headers = Headers()
    headers.add('recorder_key', encode_recorder_key(recorder.uid))

    with app.test_request_context(path='/test', headers=headers):
        assert test_endpoint() == 'Success'
        assert hasattr(flask.g, 'recorder')
        assert flask.g.recorder.uid == recorder.uid

    # incorrect recorder key
    headers.clear()
    headers.add('recorder_key', encode_recorder_key("Recorder13"))
    with app.test_request_context(path='/test', headers=headers):
        try:
            test_endpoint()
            raise AssertionError
        except:
            pass
