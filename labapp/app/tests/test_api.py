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


@pytest.mark.parametrize('attributes,data_len', [
    ({'recorder_uid': "Recorder1"}, 2),
    ({'created_from': DATESTRINGS['10_days_ago']}, 2),
    ({'created_to': DATESTRINGS['now']}, 3),
    ({'created_from': DATESTRINGS['10_days_ago'],
      'created_to': DATESTRINGS['now']}, 1),
    ({'duration': '1'}, 2),
    ({'samplerate': '10000'}, 2),
    ({'channels': '1'}, 4),
    ({'amplification': '1'}, 2)
])
@pytest.mark.usefixtures('database')
def test_getting_serieses(app, client, database, attributes, data_len):
    params_set_1 = models.RecordingParametersFactory.create(
        uid="ParametersSet1",
        samplerate=10000, channels=1, duration=1.0, amplification=1.0
    )
    params_set_2 = models.RecordingParametersFactory.create(
        uid="ParametersSet2",
        samplerate=22050, channels=1, duration=6.5, amplification=0.9
    )
    recorder_1 = models.RecorderFactory.create(uid="Recorder1")
    recorder_2 = models.RecorderFactory.create(uid="Recorder2")
    series_1 = models.SeriesFactory.create(
        created_at=NOW - timedelta(days=30), recorder=recorder_1,
        parameters=params_set_1)
    series_2 = models.SeriesFactory.create(
        created_at=NOW - timedelta(days=11), recorder=recorder_2,
        parameters=params_set_1)
    series_3 = models.SeriesFactory.create(
        created_at=NOW - timedelta(days=10), recorder=recorder_2,
        parameters=params_set_2)
    series_4 = models.SeriesFactory.create(
        created_at=NOW + timedelta(days=2), recorder=recorder_1,
        parameters=params_set_2)
    recorder_1.current_series_uid = series_1.uid
    database.session.commit()
    parameters_string = '&'.join([k + '=' + v for k, v in attributes.items()])
    response = client.get(f"{BASE_URL}/series?{parameters_string}")
    assert response.status_code == 200
    data = json.loads(response.data)
    print(data)
    assert len(data) == data_len


@pytest.mark.usefixtures('database')
def test_add_series_with_existing_parameters(app, client):
    recorder = models.RecorderFactory.create()
    parameters = models.RecordingParametersFactory.create()
    new_series = creators.create_series(recorder_uid=recorder.uid,
                                        parameters=parameters.uid)[0]
    response = client.post(
        f"{BASE_URL}/series",
        data=json.dumps(new_series),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['recorder_uid'] == recorder.uid
    assert data['parameters_uid'] == parameters.uid
    assert data['parameters']['samplerate'] == parameters.samplerate
    assert data['parameters']['channels'] == parameters.channels
    assert data['parameters']['duration'] == parameters.duration
    assert data['parameters']['amplification'] == parameters.amplification


@pytest.mark.usefixtures('database')
def test_add_series_with_uid_of_non_existing_parameters(app, client):
    recorder = models.RecorderFactory.create()
    new_series = creators.create_series(recorder_uid=recorder.uid,
                                        parameters="RP1")[0]
    response = client.post(
        f"{BASE_URL}/series",
        data=json.dumps(new_series),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['recorder_uid'] == recorder.uid
    assert data['parameters_uid'] == "RP1"
    assert data['parameters']


@pytest.mark.usefixtures('database')
def test_add_series_with_parameters_dictionary(app, client):
    recorder = models.RecorderFactory.create()
    parameters = {
        'uid': "RP1",
        'samplerate': 22222,
        'duration': 13.2
    }
    new_series = creators.create_series(recorder_uid=recorder.uid,
                                        parameters=parameters)[0]
    response = client.post(
        f"{BASE_URL}/series",
        data=json.dumps(new_series),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['recorder_uid'] == recorder.uid
    assert data['parameters_uid'] == "RP1"
    assert data['parameters']['samplerate'] == 22222
    assert data['parameters']['channels'] is not None
    assert data['parameters']['duration'] == 13.2
    assert data['parameters']['amplification'] is not None


@pytest.mark.usefixtures('database')
def test_add_series_with_parameters_dictionary_with_existing_uid(app, client):
    recorder = models.RecorderFactory.create()
    existing_parameters = models.RecordingParametersFactory.create(uid="RP1")
    parameters = {
        'uid': "RP1",
        'samplerate': 22222,
        'duration': 13.2
    }
    new_series = creators.create_series(recorder_uid=recorder.uid,
                                        parameters=parameters)[0]
    response = client.post(
        f"{BASE_URL}/series",
        data=json.dumps(new_series),
        content_type='application/json'
    )
    assert response.status_code == 400


@pytest.mark.usefixtures('database')
def test_get_series(app, client):
    series = models.SeriesFactory.create()
    response = client.get(
        f"{BASE_URL}/series/{series.uid}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == series.uid
    assert data['recorder_uid'] == series.recorder.uid
    assert data['description'] == series.description
    assert data['parameters']['samplerate'] == series.parameters.samplerate
    assert data['parameters']['channels'] == series.parameters.channels
    assert data['parameters']['duration'] == series.parameters.duration
    assert data['parameters']['amplification'] == \
        series.parameters.amplification


@pytest.mark.usefixtures('database')
def test_updating_clean_series(app, client, database):
    series = models.SeriesFactory.create()
    recorder = models.RecorderFactory()
    response = client.put(
        f"{BASE_URL}/series/{series.uid}",
        data=json.dumps(
            {'description': 'ASD', 'recorder_uid': recorder.uid}
        ),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == series.uid
    assert data['recorder_uid'] == recorder.uid
    assert data['description'] == 'ASD'


@pytest.mark.usefixtures('database')
def test_updating_non_clean_series(app, client, database):
    series = models.SeriesFactory.create()
    record = models.RecordFactory.create(series=series)
    recorder = models.RecorderFactory()
    response = client.put(
        f"{BASE_URL}/series/{series.uid}",
        data=json.dumps(
            {'recorder_uid': recorder.uid}
        ),
        content_type='application/json'
    )
    assert response.status_code == 400


@pytest.mark.usefixtures('database')
def test_deleting_clean_series(app, client, database):
    series = models.SeriesFactory.create()
    response = client.delete(
        f"{BASE_URL}/series/{series.uid}",
    )
    assert response.status_code == 204


@pytest.mark.usefixtures('database')
def test_deleting_non_clean_series(app, client, database):
    series = models.SeriesFactory.create()
    record = models.RecordFactory.create(series=series)
    response = client.delete(
        f"{BASE_URL}/series/{series.uid}",
    )
    assert response.status_code == 400


@pytest.mark.usefixtures('database')
def test_deleting_currently_maintained_series(app, client, database):
    series = models.SeriesFactory.create()
    recorder = series.recorder
    recorder.current_series_uid = series.uid
    database.session.commit()
    response = client.delete(
        f"{BASE_URL}/series/{series.uid}",
    )
    assert response.status_code == 400


@pytest.mark.usefixtures('database')
def test_getting_series_parameters(app, client):
    series = models.SeriesFactory.create()
    response = client.get(
        f"{BASE_URL}/series/{series.uid}/parameters"
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == series.parameters.uid
    assert data['samplerate'] == series.parameters.samplerate


@pytest.mark.usefixtures('database')
def test_updating_series_parameters_with_new_parameters(app, client):
    series = models.SeriesFactory.create()
    new_parameters = creators.create_recording_parameters()[0]
    response = client.put(
        f"{BASE_URL}/series/{series.uid}/parameters",
        data=json.dumps(new_parameters),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == new_parameters['uid']
    assert data['samplerate'] == new_parameters['samplerate']
    assert data['channels'] == new_parameters['channels']
    assert data['duration'] == new_parameters['duration']
    assert data['amplification'] == new_parameters['amplification']


@pytest.mark.usefixtures('database')
def test_updating_series_parameters_with_uid_of_existing(app, client):
    series = models.SeriesFactory.create()
    existing_parameters = models.RecordingParametersFactory.create()
    response = client.put(
        f"{BASE_URL}/series/{series.uid}/parameters",
        data=json.dumps(existing_parameters.uid),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['uid'] == existing_parameters.uid
    assert data['samplerate'] == existing_parameters.samplerate
    assert data['channels'] == existing_parameters.channels
    assert data['duration'] == existing_parameters.duration
    assert data['amplification'] == existing_parameters.amplification


@pytest.mark.usefixtures('database')
def test_updating_series_parameters_with_uid_of_non_existing(app, client):
    series = models.SeriesFactory.create()
    response = client.put(
        f"{BASE_URL}/series/{series.uid}/parameters",
        data=json.dumps("non_existing_uid"),
        content_type='application/json'
    )
    assert response.status_code == 404


@pytest.mark.usefixtures('database')
def test_updating_series_parameters_with_dict_containing_existing_uid(app, client):
    series = models.SeriesFactory.create()
    existing_parameters = models.RecordingParametersFactory.create()
    new_parameters = {"uid": existing_parameters.uid, 'samplerate': 23000}
    response = client.put(
        f"{BASE_URL}/series/{series.uid}/parameters",
        data=json.dumps(new_parameters),
        content_type='application/json'
    )
    assert response.status_code == 400
