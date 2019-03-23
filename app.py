import os
from flask import Flask

from  models import db

POSTGRES = {
    'user': 'postgres',
    'pw': 'password',
    'db': 'mydb',
    'host': 'localhost',
    'port': '5432',
}

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db.init_app(app)


@app.route('/')
def hello():
	return "<h1>hello world</h1>"

@app.route('/<name>')
def name_print(name):
	return "<h1>Hello {}</h1>".format(name)


if __name__ == '__main__':
	app.run()