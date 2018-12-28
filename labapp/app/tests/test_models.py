from datetime import datetime
from time import time

import pytest
from sqlalchemy.orm import exc

from app.models import Label, Record, Recorder, RecordingParameters, Series
from app.tests.fact import models


def test_label(database):
    label = Label(uid='blacklabel',
                  description='Special label for special society')
    database.session.add(label)
    database.session.commit()
    assert label.uid == 'blacklabel'
    assert label.description == 'Special label for special society'
    assert label.created_at is not None
    assert label.records == []

    # missing all parameters
    label = Label()
    database.session.add(label)
    database.session.commit()
    assert label.uid is not None
    assert label.description == ''
    assert label.created_at is not None
    assert label.records == []


def test_recorder(database):
    recorder = Recorder(uid='test_recorder', location_description='On table')
    database.session.add(recorder)
    database.session.commit()
    assert recorder.uid == 'test_recorder'
    assert recorder.location_description == 'On table'
    assert recorder.created_at is not None
    assert recorder.current_series_uid is None
    assert recorder.serieses == []

    # test adding related serieses
    series1 = Series(recorder=recorder)
    series2 = Series(recorder=recorder)
    database.session.add(series1)
    database.session.add(series2)
    database.session.commit()
    assert len(recorder.serieses) == 2

    # test setting current series from managed serieses
    recorder.current_series_uid = series1.uid
    database.session.commit()
    assert recorder.current_series_uid == series1.uid

    # test getting current series
    current_series = recorder.current_series
    assert current_series.uid == series1.uid

    # test setting non existing series as current series
    with pytest.raises(exc.NoResultFound):
        recorder.current_series_uid = 'non-existing-series'

    # test setting existing series but not maintained by current recorder
    other_recorder = Recorder(uid='other_recorder')
    seriesx = Series(recorder_uid=other_recorder.uid)
    database.session.add(other_recorder)
    database.session.add(seriesx)
    database.session.commit()
    with pytest.raises(ValueError):
        recorder.current_series_uid = seriesx.uid


def test_recording_parameters(database):
    parameters = RecordingParameters(samplerate=22100, channels=4,
                                     duration=11.01, amplification=0.98811)
    database.session.add(parameters)
    database.session.commit()
    assert parameters.uid is not None
    assert parameters.created_at is not None
    assert parameters.samplerate == 22100
    assert parameters.channels == 4
    assert parameters.duration == 11.01
    assert parameters.amplification == 0.98811

    # test setting negative samplerate
    with pytest.raises(ValueError):
        parameters.samplerate = -12222

    # test setting negative channels
    with pytest.raises(ValueError):
        parameters.channels = -1

    # test setting negative duration
    with pytest.raises(ValueError):
        parameters.duration = -12.0

    # test setting negative samplerate
    with pytest.raises(ValueError):
        parameters.amplification = -0.2


def test_series(database):
    recorder = Recorder()
    parameters = RecordingParameters()
    database.session.add_all([recorder, parameters])
    database.session.commit()
    series = Series(uid='SeriesX', description='Some series',
                    parameters_uid=parameters.uid, recorder_uid=recorder.uid)
    database.session.add(series)
    database.session.commit()
    assert series.uid is not None
    assert series.created_at is not None
    assert series.parameters == parameters
    assert series.recorder == recorder
    assert series.records == []


def test_record(database):
    recorder = Recorder(uid="RecorderX")
    parameters = RecordingParameters(uid="ParametersX", duration=100.0)
    series = Series(uid="SeriesX", recorder_uid=recorder.uid,
                    parameters_uid=parameters.uid)
    database.session.add_all([recorder, parameters, series])
    record = Record(uid='SuperQualityRecord', start_time=time(),
                    series_uid=series.uid)
    database.session.add(record)
    database.session.commit()
    assert record.uid == 'SuperQualityRecord'
    assert record.created_at is not None
    assert record.start_time < time()
    assert record.stop_time == record.start_time + parameters.duration
    assert record.uploaded_at is None
    assert record.series == series
    assert record.label is None
    assert not record.is_uploaded()
    assert record.filepath is not None
    assert not record.filepath.exists()

    # fake upload file
    record.filepath.parent.mkdir(parents=True, exist_ok=True)
    record.filepath.touch()
    record.uploaded_at = datetime.now()
    database.session.commit()
    assert record.is_uploaded()
    record.filepath.unlink()
    record.uploaded_at = None
    database.session.commit()

    
