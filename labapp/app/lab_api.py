import flask

from app import app

@app.route('/')
def index():
	return "Yo"