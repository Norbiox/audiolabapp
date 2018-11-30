import factory
from datetime import datetime, timedelta

from app.tests.factory import fake
from app.models import db, Record, Recorder, Series


class Record(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Record
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    series_uid = factory.SubFactory('app.tests.factory.models.SeriesFactory')
    duration = 25.12
    start_time = datetime.now() - timedelta(days=1)
    uploaded_at = None
    filepath = None
    label = fake.word(['GOOD', 'WRONG'])


class Recorder(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Recorder
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: "Recorder{n}".format(n))
    location_description = fake.sentence()


class Series(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Series
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    recorder_uid = factory.SubFactory('app.tests.factory.models.SeriesFactory')
    name = factory.Sequence(lambda n: "Series{n}".format(n))
    description = fake.sentence()
    samplerate = 44100
    channels = 1
    min_duration = 20
    max_duration = 30
