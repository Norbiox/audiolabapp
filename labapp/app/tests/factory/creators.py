from datetime import timedelta

from app.tests.factory import fake


def create_recorder(name=None, location_description=None):
    return {
        "name": name or "Recorder0",
        "location_description": location_description or fake.sentence()
    }


def create_record(series_uid=None, duration=None, start_time=None,
                  uploaded_at=None, filepath=None, label=None):
    datetime = fake.past_datetime(start_date="-30d", tzinfo=None)
    return {
        "series_uid": series_uid or "Series0",
        "duration": duration or 20.0,
        "start_time": datetime,
        "uploaded_at": datetime + timedelta(minutes=6),
        "filepath": fake.file_path(extension='.wav'),
        "label": fake.word(['GOOD', 'WRONG'])
    }
