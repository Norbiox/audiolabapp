import random
from datetime import datetime, timedelta

from ..fact import fake


def create_record(count=1, series_uid=None, current_series_uid=None,
                  start_time=None, uploaded_at=None, filepath=None,
                  label=None):
    if series_uid in None:
        series = create_series()["uid"]
    return [{
        "series_uid": series_uid or series["uid"],
        "current_series_uid": current_series_uid or series["uid"],
        "start_time": start_time or datetime - timedelta(minutes=5),
        "uploaded_at": uploaded_at,
        "filepath": filepath,
        "label_uid": label or fake.word(['normal', 'anomaly'])
    } for _ in range(count)]


def create_recorder(count=1, uid=None, location_description=None,
                    current_series_uid=None):
    return [{
        "uid": uid or "Recorder0",
        "location_description": location_description or fake.sentence()
    } for _ in range(count)]


def create_recording_parameters(count=1, samplerate=None, channels=None,
                                duration=None, amplification=None):
    return [{
        'samplerate': samplerate or random.randrange(1, 100000),
        'channels': channels or random.randrange(1, 10),
        'duration': round(duration or random.random() * 10, 5),
        'amplification': round(amplification or random.random() * 3, 5)
    }]


def create_series(count=1):
    pass
