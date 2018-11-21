from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Recorder(db.Model):
	__tablename__ = 'recorder'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	uid = db.Column(db.String(5), index=True)
	location_description = db.Column(db.String(100), nullable=True)

	def to_dict(self):
		return {
			'uid' : self.uid,
			'location_description': self.location_description
		}


class Series(db.Model):
	__tablename__ = 'series'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	created_at = db.Column(db.DateTime, default=db.func.now())

	uid = db.Column(db.String(5), index=True)
	min_duration = db.Column(db.Numeric(precision=10, scale=7, asdecimal=False))
	max_duration = db.Column(db.Numeric(precision=10, scale=7, asdecimal=False))


class Label(db.Model):
	__tablename__ = 'label'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	uid = db.Column(db.String(20), nullable=True)
	created_at = db.Column(db.DateTime, default=db.func.now())

	records = db.relationship('Record', backref='label', lasy=True)


class Record(db.Model)`:
	__tablename__ = 'record'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	uid = db.Column(db.String(20), index=True)
	duration = db.Column(db.Numeric(precision=10, scale=7, asdecimal=False))
	samplerate = db.Column(db.Integer)
	channels = db.Column(db.Integer)
	start_time = db.Column(db.DateTime)
	uploaded_at = db.Column(db.DateTime, default=db.func.now())
	filepath = db.Column(db.String, nullable=True)

	label_id = db.Column(db.Integer, db.ForeignKey(label.id), nullable=False)

	@property
	def stop_time(self):
		return start_time + timedelta(seconds=self.duration)