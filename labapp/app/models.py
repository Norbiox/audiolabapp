import uuid

from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql import select

from .helpers import get_object

db = SQLAlchemy()


class Label(db.Model):
    __tablename__ = 'label'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(
        db.String(36), nullable=False, unique=True, default=uuid.uuid4
    )
    created_at = db.Column(db.DateTime, default=db.func.now())
    description = db.Column(db.String(100), default="")

    records = db.relationship("Record", back_populates="label")

    def to_dict(self):
        return {
            'uid': self.uid,
            'created_at': self.created_at,
            'description': self.description
        }


@event.listens_for(Label.__table__, 'after_create')
def create_labels(*args, **kwargs):
    db.session.add(Label(
        uid='normal', description='Record of normal state'
    ))
    db.session.add(Label(
        uid='anomaly', description='Record of anomalied state'
    ))
    db.session.commit()


class Record(db.Model):
    __tablename__ = 'record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(36), unique=True, nullable=False,
                    default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=db.func.now())
    start_time = db.Column(db.Numeric(precision=17, scale=7, asdecimal=False),
                           nullable=False)
    uploaded_at = db.Column(db.DateTime)

    series_uid = db.Column(db.String(36), db.ForeignKey('series.uid'),
                           nullable=False)
    series = db.relationship("Series", back_populates="records")

    label_uid = db.Column(db.String(36), db.ForeignKey('label.uid'),
                          nullable=True, default=None)
    label = db.relationship("Label", back_populates="records")

    @hybrid_property
    def filepath(self):
        filename = str(self.uid) + ".wav"
        return app.config["UPLOADS_DEFAULT_DEST"] / \
            str(self.series.uid) / \
            filename

    @hybrid_property
    def stop_time(self):
        return self.start_time + self.series.parameters.duration

    @stop_time.expression
    def stop_time(cls):
        return select(cls.start_time + RecordingParameters.duration).\
            where(RecordingParameters.uid == Series.parameters_uid).\
            where(Series.uid == cls.series_uid).\
            as_scalar()

    def is_uploaded(self):
        return self.uploaded_at is not None and self.filepath.exists()

    def to_dict(self):
        return {
            'uid': self.uid,
            'created_at': self.created_at,
            'series_uid': self.series_uid,
            'label_uid': self.label_uid,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'uploaded_at': self.uploaded_at
        }


class Recorder(db.Model):
    __tablename__ = 'recorder'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(36), unique=True, index=True, nullable=False,
                    default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=db.func.now())
    location_description = db.Column(db.String(100), default="")

    current_series_uid = db.Column(db.String(36), nullable=True, default=None)

    serieses = db.relationship("Series", back_populates="recorder")

    @hybrid_property
    def current_series(self):
        if self.current_series_uid is not None:
            try:
                return Series.query.filter_by(
                    uid=self.current_series_uid
                ).one()
            except orm.exc.NoResultFound:
                pass
        return None

    @validates('current_series_uid')
    def validate_current_series_uid(self, key, current_series_uid):
        if current_series_uid is not None:
            series = get_object(Series, current_series_uid)
            if series.recorder_uid != self.uid:
                raise ValueError(
                    "Series with uid {} is not maintaned by recorder {}".
                    format(series.uid, self.uid)
                )
            return series.uid
        return None

    def to_dict(self):
        return {
            'uid': self.uid,
            'created_at': self.created_at,
            'location_description': self.location_description,
            'current_series_uid': self.current_series_uid
        }


class RecordingParameters(db.Model):
    __tablename__ = 'recording_parameters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(36), unique=True, nullable=False,
                    default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=db.func.now())
    samplerate = db.Column(db.Integer, default=44100)
    channels = db.Column(db.Integer, default=1)
    duration = db.Column(db.Numeric(precision=13, scale=7, asdecimal=False),
                         default=5.0)
    amplification = db.Column(
        db.Numeric(precision=10, scale=7, asdecimal=False),
        default=1.0
    )

    serieses = db.relationship("Series", back_populates="parameters")

    @validates('samplerate')
    def validate_samplerate(self, key, samplerate):
        if samplerate <= 0:
            raise ValueError("Samplerate must be more than zero")
        return samplerate

    @validates('channels')
    def validate_channels(self, key, channels):
        if channels <= 0:
            raise ValueError("Channels number must be more than zero")
        return channels

    @validates('duration')
    def validate_duration(self, key, duration):
        if duration <= 0:
            raise ValueError("Duration must be more than zero")
        return duration

    @validates('amplification')
    def validate_amplification(self, key, amplification):
        if amplification <= 0:
            raise ValueError("Amplification must be more than zero")
        return amplification

    def to_dict(self):
        return {
            'uid': self.uid,
            'created_at': self.created_at,
            'samplerate': self.samplerate,
            'channels': self.channels,
            'duration': self.duration,
            'amplification': self.amplification
        }


class Series(db.Model):
    __tablename__ = 'series'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(36), unique=True, nullable=False,
                    default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=db.func.now())
    description = db.Column(db.String(255), nullable=True)

    parameters_uid = db.Column(db.String(36),
                               db.ForeignKey('recording_parameters.uid'))
    parameters = db.relationship("RecordingParameters",
                                 back_populates="serieses")

    recorder_uid = db.Column(db.String(36), db.ForeignKey('recorder.uid'),
                             nullable=False)
    recorder = db.relationship("Recorder", back_populates="serieses")

    records = db.relationship("Record", back_populates="series",
                              cascade="save-update, merge, delete")

    def to_dict(self):
        return {
            'uid': self.uid,
            'created_at': self.created_at,
            'recorder_uid': self.recorder.uid,
            'description': self.description,
            'parameters_uid': self.parameters_uid,
            'parameters': self.parameters.to_dict()
            if self.parameters else None
        }
