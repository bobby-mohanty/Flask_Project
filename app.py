
import os
import json
import requests
import operator
import re
import nltk

from rq import Queue
from rq.job import Job
from flask import Flask, render_template, request, jsonify
from collections import Counter
from bs4 import BeautifulSoup

from models import db
from models import Result
from stop_words import stops
from worker import conn

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
app.app_context().push()

q = Queue(connection=conn)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    if 'http://' not in url[:7]:
        url = 'http://' + url
    # start job
    job = q.enqueue_call(
        func=count_and_save_words, args=(url,), result_ttl=5000
    )
    # return created job id
    return job.get_id()

def count_and_save_words(url):
    errors = list()
    try:
        r = requests.get(url)
    except:
        errors.append("Unable to get URL {}".format(url))
        return dict(error=errors)

    # text processing
    raw = BeautifulSoup(r.text, 'html.parser').get_text()
    nltk.data.path.append('./nltk_data/')
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)

    # remove punctuations, count raw words
    nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if nonPunct.match(w)]
    raw_word_count = Counter(raw_words)

    # stop words
    no_stop_words = [w for w in raw_words if w.lower() not in stops]
    no_stop_words_count = Counter(no_stop_words)

    # save results
    try:
        result = Result(
            url=url,
            result_all=raw_word_count,
            result_no_stop_words=no_stop_words_count
        )
        db.session.add(result)
        db.session.commit()
        return result.id
    except Exception as e:
        print("*" * 100)
        print(e)
        errors.append("Unable to add item to database.")
        return {'error': errors}


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
            result.result_no_stop_words.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        return jsonify(results)
    else:
        return "Nay!", 202


if __name__ == '__main__':
    app.run()
