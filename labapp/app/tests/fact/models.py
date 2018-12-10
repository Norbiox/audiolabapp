import factory
from random import choice

from ..fact import fake
from app.models import db, Record, Recorder, RecordingParameters, Series


class RecordFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Record
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    created_at = fake.date_time_this_year(before_now=True, after_now=False)
    series = factory.SubFactory('app.tests.fact.models.SeriesFactory')
    start_time = fake.date_time_this_year(before_now=True, after_now=False)
    uploaded_at = None
    filepath = None
    label_uid = choice(['normal', 'anomaly', None])


class RecorderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Recorder
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    uid = factory.Sequence(lambda n: f"Recorder{n}")
    created_at = fake.date_time_this_year(before_now=True, after_now=False)
    location_description = fake.sentence()
    current_series_uid = None


class RecordingParametersFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RecordingParameters
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    uid = factory.Sequence(lambda n: f"ParametersSet{n}")
    created_at = fake.date_time_this_year(before_now=True, after_now=False)
    samplerate = 44100
    channels = 1
    duration = 10.0
    amplification = 1.1

    @factory.post_generation
    def serieses(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for n in extracted:
                self.serieses.append(n)


class SeriesFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Series
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    uid = factory.Sequence(lambda n: f"Series{n}")
    created_at = fake.date_time_this_year(before_now=True, after_now=False)
    description = fake.sentence()
    recorder = factory.SubFactory(
        'app.tests.fact.models.RecorderFactory'
    )
    parameters = factory.SubFactory(
        'app.tests.fact.models.RecordingParametersFactory'
    )

    @factory.post_generation
    def records(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for n in extracted:
                self.serieses.append(n)
