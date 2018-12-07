import json
from datetime import datetime, timedelta

import pytest

from app.helpers import datetime_to_string
from app.models import Label, Record, Recorder, RecordingParameters, Series
from app.tests.fact import fake, models, creators


BASE_URL = '1.0/lab'

NOW = datetime.now()
DATESTRINGS = {
    'now': datetime_to_string(NOW),
    '10_days_ago': datetime_to_string(NOW - timedelta(days=10)),
    '30_days_ago': datetime_to_string(NOW - timedelta(days=30))
}


@pytest.mark.parametrize('attributes,data_len', [
    ({'created_from': DATESTRINGS['10_days_ago']}, 2),
    ({'created_to': DATESTRINGS['now']}, 2),
    ({'created_from': DATESTRINGS['10_days_ago'],
      'created_to': DATESTRINGS['now']}, 1),
    ({'busy': 'true'}, 1),
    ({'busy': 'false'}, 2)
])
@pytest.mark.usefixtures('database')
def test_getting_recorders(app, client, database, attributes, data_len):
    helper_series = models.SeriesFactory()
    helper_series2 = models.SeriesFactory(recorder=helper_series.recorder)
    recorder1 = helper_series.recorder
    recorder1.current_series_uid = helper_series.uid
    recorder1.created_at = datetime.now() - timedelta(days=30)
    database.session.commit()
    recorder2 = models.RecorderFactory.create(
        created_at=NOW - timedelta(days=10),
    )
    recorder3 = models.RecorderFactory.create(
        created_at=NOW + timedelta(days=2)
    )
    parameters_string = '&'.join([k + '=' + v for k, v in attributes.items()])
    response = client.get(f"{BASE_URL}/recorder?{parameters_string}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == data_len


@pytest.mark.usefixtures('database')
def test_adding_recorder(app, client):
    new_recorder = creators.create_recorder()[0]
    response = client.post(
        f"{BASE_URL}/recorder",
        data=json.dumps(new_recorder),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['location_description'] == new_recorder['location_description']
    assert data['current_series_uid'] is None


@pytest.mark.usefixtures('database')
def test_getting_recorder(app, client):
    recorder = models.RecorderFactory.create()
    response = client.get(
        f"{BASE_URL}/recorder/{recorder.uid}"
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == recorder.uid
    assert data['location_description'] == recorder.location_description


@pytest.mark.usefixtures('database')
def test_updating_recorder(app, client):
    recorder = models.RecorderFactory.create()
    response = client.put(
        f"{BASE_URL}/recorder/{recorder.uid}",
        data=json.dumps({'location_description': 'Some crazy location'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == recorder.uid
    assert data['location_description'] == "Some crazy location"


@pytest.mark.usefixtures('database')
def test_getting_recorders_current_series(app, client, database):
    series = models.SeriesFactory.create()
    recorder = series.recorder
    recorder.current_series_uid = series.uid
    database.session.commit()
    response = client.get(f"{BASE_URL}/recorder/{recorder.uid}/current_series")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == series.uid


@pytest.mark.usefixtures('database')
def test_setting_recorders_current_series(app, client):
    recorder = models.RecorderFactory.create()
    series = models.SeriesFactory.create(recorder=recorder)
    response = client.put(
        f"{BASE_URL}/recorder/{recorder.uid}/current_series" +
        f"?series_uid={series.uid}",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == series.uid
    # unsetting series
    response = client.put(
        f"{BASE_URL}/recorder/{recorder.uid}/current_series",
    )
    assert response.status_code == 204


@pytest.mark.usefixtures('database')
def test_get_recording_parameters_sets(app, client):
    models.RecordingParametersFactory.create_batch(5)
    response = client.get('{base_url}/parameters'.format(base_url=BASE_URL))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 5


@pytest.mark.parametrize('attributes,data_len', [
    ({'created_from': DATESTRINGS['10_days_ago']}, 6),
    ({'created_to': DATESTRINGS['now']}, 3),
    ({'created_from': DATESTRINGS['10_days_ago'],
      'created_to': DATESTRINGS['now']}, 2),
    ({'samplerate': '22050'}, 6),
    ({'channels': '1'}, 5),
    ({'duration': '10.2'}, 2),
    ({'amplification': '1.5'}, 3)
])
@pytest.mark.usefixtures('database')
def test_get_recording_parameters_sets_filtering(app, client, attributes,
                                                 data_len):
    models.RecordingParametersFactory.create_batch(
        1, created_at=NOW - timedelta(days=30),
        samplerate=44100, channels=1, duration=10.0, amplification=1.5,
    )
    models.RecordingParametersFactory.create_batch(
        2, created_at=NOW - timedelta(days=10),
        samplerate=22050, channels=2, duration=10.2, amplification=1.5,
    )
    models.RecordingParametersFactory.create_batch(
        4, created_at=NOW + timedelta(days=2),
        samplerate=22050, channels=1, duration=7.114, amplification=1.1,
    )
    parameters_string = '&'.join([k + '=' + v for k, v in attributes.items()])
    response = client.get(f"{BASE_URL}/parameters?{parameters_string}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == data_len


@pytest.mark.usefixtures('database')
def test_add_recording_parameters(app, client):
    new_parameters = creators.create_recording_parameters()[0]
    response = client.post(
        f"{BASE_URL}/parameters",
        data=json.dumps(new_parameters),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['samplerate'] == new_parameters['samplerate']
    assert data['channels'] == new_parameters['channels']
    assert data['duration'] == new_parameters['duration']
    assert data['amplification'] == new_parameters['amplification']

    # adding similar parameters set should end with returning existing set
    # without adding new
    previously_added_parameters_uid = data['uid']
    response = client.post(
        f"{BASE_URL}/parameters",
        data=json.dumps(new_parameters),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == previously_added_parameters_uid

    # cannot duplicate uid
    data['samplerate'] = data['samplerate'] * 2
    response = client.post(
        f"{BASE_URL}/parameters",
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 400


@pytest.mark.usefixtures('database')
def test_get_recording_parameters(app, client):
    parameters_set = models.RecordingParametersFactory.create(
        created_at=NOW - timedelta(days=30),
        samplerate=44100, channels=1, duration=2.0, amplification=1.5,
    )
    response = client.get(
        f"{BASE_URL}/parameters/{parameters_set.uid}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['samplerate'] == 44100
    assert data['channels'] == 1
    assert data['duration'] == 2.0
    assert data['amplification'] == 1.5


@pytest.mark.usefixtures('database')
def test_delete_recording_parameters(app, client):
    parameters_set = models.RecordingParametersFactory.create(
        created_at=NOW - timedelta(days=30),
        samplerate=44100, channels=1, duration=2.0, amplification=1.5,
    )
    response = client.delete(f"{BASE_URL}/parameters/{parameters_set.uid}")
    assert response.status_code == 204
    sets = RecordingParameters.query.filter_by(uid=parameters_set.uid)
    assert len(sets.all()) == 0
    # TODO: assert that it's impossible to delete parameters of existing
    #       series


@pytest.mark.usefixtures('database')
def test_getting_serieses(app, client):
    series = models.SeriesFactory.create()
