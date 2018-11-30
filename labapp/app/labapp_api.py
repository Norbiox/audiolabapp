import flask
from connexion import request
from sqlalchemy import and_, exc, orm

from .models import db, Record, Recorder, RecordingParameters, Series


def get_records(series_uid=None, parameters_uid=None, recorded_from=None,
                recorded_to=None, uploaded=None, label=None,):
    return []


def new_record():
    return {}


def get_record(record_uid):
    return {}


def delete_record(record_uid):
    return {}


def update_records_label(record_uid, label_uid):
    return {}


def get_record_parameters(record_uid):
    return {}


def download_record(record_uid):
    return []


def upload_record(record_uid, recorder_key):
    return {}


def get_recorders(series_uid=None, created_from=None, created_to=None,
                  busy=None):
    return []


def new_recorder():
    recorder_data = request.get_json()
    try:
        recorder = Recorder(
            location_description=recorder_data['location_description']
        )
        db.session.add(recorder)
        db.session.commit()
        return recorder.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, 'Bad request')
    except ValueError as ex:
        flask.abort(400, str(ex))


def get_recorder(recorder_uid):
    try:
        recorder = Recorder.query.filter(Recorder.uid == recorder_uid).one()
        return recorder.to_dict()
    except orm.exc.NoResultFound:
        flask.abort(404, 'Recorder not found')


def update_recorder(recorder_uid):
    recorder_data = request.get_json()
    try:
        recorder = Recorder.query.filter(Recorder.uid == recorder_uid).one()
        recorder.update(
            location_description=recorder_data['location_description'])
        db.session.commit()
        return recorder.to_dict()
    except orm.exc.NoResultFound:
        flask.abort(404, 'Recorder not found')
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, 'Bad request')
    except ValueError as ex:
        flask.abort(400, str(ex))


def get_current_series(recorder_uid):
    return {}


def set_current_series(recorder_uid, series_uid):
    return {}


def unset_current_series(recorder_uid):
    return {}


def get_recording_parameters_sets(series_uid=None, created_from=None,
                                  created_to=None, samplerate=None,
                                  channels=None, duration=None,
                                  amplification=None):
    return []


def new_recording_parameters():
    return {}


def get_recording_parameters(parameters_uid):
    return {}


def delete_recording_parameters(parameters_uid):
    return {}


def get_serieses(recorder_uid=None, created_from=None, created_to=None,
                 min_duration=None, max_duration=None, samplerate=None,
                 channels=None, amplification=None):
    return []


def new_series():
    return {}


def get_series(series_uid):
    return {}


def update_series(series_uid):
    return {}


def delete_series(series_uid):
    return {}
