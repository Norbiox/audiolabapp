import flask
from connexion import request
from sqlalchemy import and_, exc, orm, or_

from app.decorators import recorder_required
from app.helpers import (
    get_object, get_object_or_404, increase_last_digit, parse_filtering_dates
)
from app.models import db, Label, Record, Recorder, RecordingParameters, Series


def get_labels():
    return [l.to_dict() for l in Label.query.all()]


def new_label():
    label_data = request.get_json()
    try:
        label = Label(**label_data)
        db.session.add(label)
        db.session.commit()
        return label.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))


def get_records(series_uid=None, recorded_from=None, recorded_to=None,
                uploaded=None, label=None, labeled=None):
    filters = []
    rf, rt = parse_filtering_dates(recorded_from, recorded_to, True)
    if rf:
        filters.append(Record.start_time >= rf)
    if rt:
        filters.append(Record.stop_time <= rt)
    if series_uid:
        filters.append(
            or_(*[Record.series_uid == uid for uid in series_uid])
        )
    if uploaded is not None:
        if uploaded:
            filters.append(Record.uploaded_at is not None)
        else:
            filters.append(Record.uploaded_at is None)
    if label:
        filters.append(
            or_(*[Record.label_uid == uid for uid in label])
        )
    if labeled is not None:
        if labeled:
            filters.append(Record.label_uid != None)
        else:
            filters.append(Record.label_uid == None)
    records = Record.query.filter(and_(*filters))
    return [r.to_dict() for r in records]


@recorder_required
def new_record():
    record_data = request.get_json()
    recorder = flask.g.recorder
    if record_data["series_uid"] not in [s.uid for s in recorder.serieses]:
        flask.abort(403, "Recorder {} does not maintain series {}".format(
            recorder.uid, record_data["series_uid"]
        ))
    if record_data["label_uid"] is not None:
        get_object_or_404(Label, record_data["label_uid"])
    try:
        record = Record(**record_data)
        db.session.add(record)
        db.session.commit()
        return record.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))


def get_record(record_uid):
    return get_object_or_404(Record, record_uid).to_dict()


def delete_record(record_uid):
    record = get_object_or_404(Record, record_uid)
    if record.filepath.exists():
        record.filepath.unlink()
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
    label_uid = data.pop('label_uid')
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
    record = get_object_or_404(Record, record_uid)
    if not record.is_uploaded():
        flask.abort(
            404, "This record is registered but file has not been uploaded yet"
        )
    return flask.send_file(str(record.filepath),
                           attachment_filename=record.filepath.name)


@recorder_required
def upload_record(record_uid):
    record = get_object_or_404(Record, record_uid)
    recorder = flask.g.recorder
    if record.series_uid not in [s.uid for s in recorder.serieses]:
        flask.abort(403, "Recorder {} does not maintain series {}".format(
            recorder.uid, record.series_uid
        ))
    try:
        file = request.files['file']
        if file.filename.split('.')[-1] != 'wav':
            raise TypeError("Attached file has wrong format")
    except KeyError:
        flask.abort(400, "No file has been attached to request")
    except TypeError as ex:
        flask.abort(400, str(ex))
    if record.filepath.exists():
        record.filepath.unlink()
    file.save(str(record.filepath))
    return record.to_dict()


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
    try:
        recorder = Recorder(**recorder_data)
        db.session.add(recorder)
        db.session.commit()
        return recorder.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))


def get_recorder(recorder_uid):
    return get_object_or_404(Recorder, recorder_uid).to_dict()


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


def get_serieses(recorder_uid=None, parameters_uid=None, created_from=None,
                 created_to=None, duration=None, samplerate=None,
                 channels=None, amplification=None):
    parameters_filters = []
    if samplerate:
        parameters_filters.append(
            or_(*[RecordingParameters.samplerate == s for s in samplerate])
        )
    if channels:
        parameters_filters.append(
            or_(*[RecordingParameters.channels == c for c in channels])
        )
    if duration:
        parameters_filters.append(
            or_(*[RecordingParameters.duration >= d for d in duration])
        )
        parameters_filters.append(
            or_(*[RecordingParameters.duration < increase_last_digit(d)
                  for d in duration])
        )
    if amplification:
        parameters_filters.append(
            or_(*[RecordingParameters.amplification >= a
                  for a in amplification])
        )
        parameters_filters.append(
            or_(*[RecordingParameters.amplification < increase_last_digit(a)
                  for a in amplification])
        )
    parameters = RecordingParameters.query.filter(and_(*parameters_filters))
    parameters_uids = [p.to_dict()['uid'] for p in parameters]

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
    if parameters_uid:
        parameters_uid = set(parameters_uid).intersection(parameters_uids)
    else:
        parameters_uid = parameters_uids
    filters.append(
        or_(*[Series.parameters_uid == p for p in parameters_uid])
    )
    serieses = Series.query.filter(and_(*filters))
    return [s.to_dict() for s in serieses]


def new_series():
    series_data = request.get_json()
    get_object_or_404(Recorder, series_data['recorder_uid'])
    parameters = series_data.pop('parameters')
    try:
        try:
            uid = parameters.pop('uid')
            parameters_obj = get_object(RecordingParameters, uid)
        except orm.exc.NoResultFound:
            parameters_obj = RecordingParameters(uid=uid, **parameters)
        except KeyError:
            parameters_obj = RecordingParameters(**parameters)
        db.session.add(parameters_obj)
        db.session.commit()
        series = Series(parameters_uid=parameters_obj.uid, **series_data)
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
    return get_object_or_404(Series, series_uid).to_dict()


def update_series(series_uid):
    series = get_object_or_404(Series, series_uid)
    series_data = request.get_json()
    description = series_data.pop('description', None)
    recorder_uid = series_data.pop('recorder_uid', None)
    try:
        if description is not None:
            series.description = description
        if recorder_uid is not None:
            if series.records:
                flask.abort(400,
                            "Cannot change recorder of non empty series")
            series.recorder_uid = recorder_uid
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


def get_series_parameters(series_uid):
    series = get_object_or_404(Series, series_uid)
    return series.parameters.to_dict()


def update_series_parameters(series_uid):
    series = get_object_or_404(Series, series_uid)
    parameters = request.get_json()
    try:
        uid = parameters.pop('uid')
        parameters_set = get_object(RecordingParameters, uid)
    except orm.exc.NoResultFound:
        parameters_set = RecordingParameters(uid=uid, **parameters)
    except KeyError:
        parameters_set = RecordingParameters(**parameters)
    series.parameters_uid = parameters_set.uid
    try:
        db.session.add(parameters_set)
        db.session.commit()
        return parameters_set.to_dict()
    except exc.IntegrityError as ex:
        db.session.rollback()
        flask.abort(400, str(ex))
    except ValueError as ex:
        flask.abort(400, str(ex))
