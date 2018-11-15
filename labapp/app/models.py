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