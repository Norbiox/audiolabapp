import flask
from connexion import request
from sqlalchemy import and_, exc, orm, or_

from .helpers import (
    get_object, get_object_or_404, increase_last_digit, parse_filtering_dates
)
from .models import db, Label, Record, Recorder, RecordingParameters, Series


def get_records(series_uid=None, parameters_uid=None, recorded_from=None,
                recorded_to=None, uploaded=None, label=None):
    filters = []
    rf, rt = parse_filtering_dates(recorded_from, recorded_to)
    filters.append(Record.start_time >= rf)
    filters.append(Record.start_time <= rt)
    if series_uid:
        filters.append(
            or_(*[Record.series_uid == uid for uid in series_uid])
        )
    if parameters_uid:
        filters.append(
            or_(*[Record.series.parameters_uid == uid
                  for uid in parameters_uid])
        )
    if uploaded:
        filters.append(Record.uploaded_at is not None)
    elif uploaded is not None:
        filters.append(Record.uploaded_at is None)
    if label:
        filters.append(
            or_(*[Record.label_uid == uid for uid in label])
        )
    records = Record.query.filter(and_(*filters))
    return [r.to_dict() for r in records]


def new_record():
    return {}


def get_record(record_uid):
    return get_object_or_404(Record, record_uid).to_dict()


def delete_record(record_uid):
    record = get_object_or_404(Record, record_uid)
    db.session.delete(record)
    return ('Record deleted', 204)


def get_records_label(record_uid):
    record = get_object_or_404(Record, record_uid)
    if record.label_uid is None:
        return {}
    label = get_object_or_404(Label, record.label_uid)
    return label.to_dict()


def update_records_label(record_uid):
    record = get_object_or_404(Record, record_uid)
    data = request.get_json()
    label_uid = data.put('label_uid')
    if label_uid is not None:
        get_object_or_404(Label, label_uid)
    record.label_uid = label_uid
    db.session.add(record)
    db.session.commit()
    return record.to_dict()


def get_record_parameters(record_uid):
    record = get_object_or_404(Record, record_uid)
    return record.series.parameters.to_dict()


def download_record(record_uid):
    return []


def upload_record(record_uid, recorder_key):
    return {}


def get_recorders(series_uid=None, created_from=None, created_to=None,
                  busy=None):
    filters = []
    created_from, created_to = parse_filtering_dates(created_from, created_to)
    if created_from:
        filters.append(Recorder.created_at >= created_from)
    if created_to:
        filters.append(Recorder.created_at <= created_to)
    if series_uid:
        filters.append(
            or_(*[uid in [s.uid for s in Recorder.serieses]
                  for uid in series_uid])
        )
    if busy is not None:
        if busy:
            filters.append(Recorder.current_series_uid != None)
        if not busy:
            filters.append(Recorder.current_series_uid == None)
    recorders = Recorder.query.filter(and_(*filters))
    return [r.to_dict() for r in recorders]


def new_recorder():
    recorder_data = request.get_json()
    recorder_uid = recorder_data.pop('uid')
    location_description = recorder_data.pop('location_description')
    try:
        recorder = Recorder(
            uid=recorder_uid,
            location_description=location_description
        )
        db.session.add(recorder)
        db.session.commit()
        return recorder.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))


def get_recorder(recorder_uid):
    recorder = get_object_or_404(Recorder, recorder_uid)
    return recorder.to_dict()


def update_recorder(recorder_uid):
    recorder = get_object_or_404(Recorder, recorder_uid)
    recorder_data = request.get_json()
    location_description = recorder_data.pop('location_description')
    try:
        if location_description is not None:
            recorder.location_description = location_description
        db.session.commit()
        return recorder.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))


def get_current_series(recorder_uid):
    recorder = get_object_or_404(Recorder, recorder_uid)
    series = get_object_or_404(Series, recorder.current_series_uid)
    return series.to_dict()


def set_current_series(recorder_uid, series_uid=None):
    recorder = get_object_or_404(Recorder, recorder_uid)
    print(series_uid)
    if series_uid is None:
        recorder.current_series_uid = None
        db.session.commit()
        return (f'Current series of recorder {recorder.uid} unset.', 204)
    series = get_object_or_404(Series, series_uid)
    try:
        recorder.current_series_uid = series_uid
        db.session.commit()
        return series.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))


def get_recording_parameters_sets(series_uid=None, created_from=None,
                                  created_to=None, samplerate=None,
                                  channels=None, duration=None,
                                  amplification=None):
    filters = []
    created_from, created_to = parse_filtering_dates(created_from, created_to)
    if created_from:
        filters.append(RecordingParameters.created_at >= created_from)
    if created_to:
        filters.append(RecordingParameters.created_at <= created_to)
    if series_uid:
        filters.append(
            or_(*[uid in [s.uid for s in RecordingParameters.serieses]
                  for uid in series_uid])
        )
    if samplerate:
        filters.append(
            or_(*[RecordingParameters.samplerate == s for s in samplerate])
        )
    if channels:
        filters.append(
            or_(*[RecordingParameters.channels == c for c in channels])
        )
    if duration:
        filters.append(
            or_(*[RecordingParameters.duration >= d for d in duration])
        )
        filters.append(
            or_(*[RecordingParameters.duration < increase_last_digit(d)
                  for d in duration])
        )
    if amplification:
        filters.append(
            or_(*[RecordingParameters.amplification >= a
                  for a in amplification])
        )
        filters.append(
            or_(*[RecordingParameters.amplification < increase_last_digit(a)
                  for a in amplification])
        )
    parameters_sets = RecordingParameters.query.filter(and_(*filters))
    return [ps.to_dict() for ps in parameters_sets]


def new_recording_parameters(parameters={}):
    if not parameters:
        parameters = request.get_json()
    try:
        parameters_set = RecordingParameters(**parameters)
    except ValueError as ex:
        flask.abort(400, str(ex))
    try:
        # check, if similar set does not already exist in database
        sets = RecordingParameters.query.filter(and_(*[
            RecordingParameters.samplerate == parameters_set.samplerate,
            RecordingParameters.channels == parameters_set.channels,
            RecordingParameters.duration == parameters_set.duration,
            RecordingParameters.amplification == parameters_set.amplification
        ])).one()
        return sets.to_dict()
    except orm.exc.NoResultFound:
        try:
            db.session.add(parameters_set)
            db.session.commit()
            return parameters_set.to_dict()
        except exc.IntegrityError as ex:
            db.session.rollback()
            flask.abort(400, str(ex))


def get_recording_parameters(parameters_uid):
    parameters = get_object_or_404(RecordingParameters, parameters_uid)
    return parameters.to_dict()


def delete_recording_parameters(parameters_uid):
    parameters = get_object_or_404(RecordingParameters, parameters_uid)
    db.session.delete(parameters)
    return (f'Parameters {parameters_uid} deleted', 204)


def get_serieses(recorder_uid=None, parameters_uid=None, created_from=None,
                 created_to=None, duration=None, samplerate=None,
                 channels=None, amplification=None):
    filters = []
    created_from, created_to = parse_filtering_dates(created_from, created_to)
    if created_from:
        filters.append(Series.created_at >= created_from)
    if created_to:
        filters.append(Series.created_at <= created_to)
    if recorder_uid:
        filters.append(
            or_(*[Series.recorder_uid == r for r in recorder_uid])
        )
    if any([duration, samplerate, channels, amplification]):
        parameters_sets = get_recording_parameters_sets(
            duration=duration, samplerate=samplerate, channels=channels,
            amplification=amplification
        )
        params_uids = [ps['uid'] for ps in parameters_sets]
        filters.append(
            or_(*[Series.parameters_uid == p for p in params_uids])
        )
    if parameters_uid:
        filters.append(
            or_(*[Series.parameters_uid == p for p in parameters_uid])
        )
    serieses = Series.query.filter(and_(*filters))
    return [s.to_dict() for s in serieses]


def new_series():
    series_data = request.get_json()
    parameters_uid = series_data.pop('parameters_uid', None)
    parameters = series_data.pop('parameters', None)
    if parameters:
        if parameters_uid:
            parameters['uid'] = parameters_uid
        parameters = new_recording_parameters(parameters)
    elif parameters_uid:
        if not parameters:
            parameters = {}
        try:
            parameters = get_object(
                RecordingParameters, parameters_uid
            ).to_dict()
        except orm.exc.NoResultFound:
            parameters["uid"] = parameters_uid
            parameters = new_recording_parameters(parameters)
    series_data['parameters_uid'] = parameters['uid']
    try:
        series = Series(**series_data)
        db.session.add(series)
        db.session.commit()
        return series.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))
    return {}


def get_series(series_uid):
    series = get_object_or_404(Series, series_uid)
    return series.to_dict()


def update_series(series_uid):
    series = get_object_or_404(Series, series_uid)
    series_data = request.get_json()
    description = series_data.pop('description', None)
    parameters_uid = series_data.pop('parameters_uid', None)
    try:
        if description is not None:
            series.description = description
        if parameters_uid is not None:
            if series.records:
                print(series.records)
                flask.abort(400,
                            "Cannot change parameters of non empty series")
            series.parameters_uid = parameters_uid
        db.session.commit()
        return series.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))


def delete_series(series_uid):
    series = get_object_or_404(Series, series_uid)
    if series.records:
        flask.abort(400, "Cannot delete non empty series")
    if series.recorder.current_series_uid == series.uid:
        flask.abort(400, "Cannot delete currently maintanded series")
    db.session.delete(series)
    return (f'Series {series_uid} deleted', 204)
