import jwt
import uuid
from datetime import timedelta
from passlib.apps import custom_app_context as pwd_context

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Label(db.Model):
    __tablename__ = 'record_label'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(
        db.String(10), nullable=False, unique=True, default=uuid.uuid4
    )
    created_at = db.Column(db.DateTime, default=db.func.now)
    description = db.Column(db.String(100), default="")

    records = db.relationship('Record', back_populates='label', lazy=True,
                              cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'uid': self.uid,
            'created_at': self.created_at,
            'description': self.description
        }


class Record(db.Model):
    __tablename__ = 'record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(36), unique=True, nullable=False,
                    default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=db.func.now)
    start_time = db.Column(db.DateTime)
    uploaded_at = db.Column(db.DateTime)
    filepath = db.Column(db.String)

    series_uid = db.Column(db.String, db.ForeignKey('series.uid'),
                           nullable=False)
    label_uid = db.Column(db.String, db.ForeignKey('record_label.uid'),
                          nullable=True, default=None)

    @hybrid_property
    def parameters(self):
        return self.series.parameters

    @hybrid_property
    def stop_time(self):
        return self.start_time + timedelta(seconds=self.parameters.duration)

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
    created_at = db.Column(db.DateTime, default=db.func.now)
    location_description = db.Column(db.String(100), default="")

    current_series_uid = db.Column(db.String, db.ForeignKey('series.uid'),
                                   nullable=True, default=None)

    serieses = db.relationship('Series', backref='recorder', lazy=True,
                               cascade="all, delete-orphan")

    @hybrid_property
    def current_series(self):
        try:
            return Series.query.filter_by(uid=self.current_series_uid).one()
        except orm.exc.NoResultFound:
            return None

    @validates('current_series_uid')
    def validate_actual_series_uid(self, key, current_series_uid):
        try:
            series = Series.query.filter_by(uid=current_series_uid).one()
            if series.recorder_uid != self.uid:
                raise ValueError(
                    "Series with uid {} is not maintaned by recorder {}".
                    format(series.uid, self.uid)
                )
        except orm.exc.NoResultFound:
            raise ValueError("Series with uid {} does not exists".
                             format(current_series_uid))

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
    created_at = db.Column(db.DateTime, default=db.func.now)
    samplerate = db.Column(db.Integer, default=44100)
    channels = db.Column(db.Integer, default=1)
    duration = db.Column(db.Numeric(precision=10, scale=7, asdecimal=False),
                         default=5.0)
    amplification = db.Column(
        db.Numeric(precision=10, scale=7, asdecimal=False),
        default=1.0
    )

    serieses = db.relationship('Series', backref='parameters', lazy=True,
                               cascade="all, delete-orphan")

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
    created_at = db.Column(db.DateTime, default=db.func.now)
    description = db.Column(db.String(255), nullable=True)

    parameters_uid = db.Column(db.String,
                               db.ForeignKey('recording_parameters.uid'),
                               nullable=False)
    recorder_uid = db.Column(db.String, db.ForeignKey('recorder.uid'),
                             nullable=False)
    records = db.relationship('Record', backref='series', lazy=True,
                              cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'uid': self.uid,
            'created_at': self.created_at,
            'recorder_uid': self.recorder.uid,
            'description': self.description,
            'parameters_uid': self.parameters_uid,
            'parameters': self.parameters.to_dict
        }
