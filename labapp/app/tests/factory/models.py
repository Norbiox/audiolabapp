import factory

from ...tests.factory import fake, generate_uid
from ...models import db, Label, Record, Recorder, Series

class LabelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Label
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    