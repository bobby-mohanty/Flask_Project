from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route('/')
def hello():
	return "<h1>hello world</h1>"

@app.route('/<name>')
def name_print(name):
	return "<h1>Hello {}</h1>".format(name)


if __name__ == '__main__':
	app.run()