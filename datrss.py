#from __future__ import print_function, absolute_import, division

import sqlite3
import feedparser
from contextlib import closing
import time
import json
import thread

from flask import (Flask, Response, request, session, g, redirect, url_for,
                   abort, render_template, flash)
from flask.json import JSONEncoder
from database import db_session
from models import User

# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config.from_object(__name__)
class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, time.struct_time):
           return "{}/{}/{} {}:{}:{}".format(o.tm_mon,
                                             o.tm_mday,
                                             o.tm_year,
                                             o.tm_hour,
                                             o.tm_min,
                                             o.tm_sec)
        return JSONEncoder.default(self, o)

def jsonify(data):
    return Response(json.dumps(data, cls=CustomJSONEncoder), mimetype='application/json')

app.json_encoder = CustomJSONEncoder

@app.route('/')
def root():
    """Render index.html template with list of dicts:
    {
    'headline': headline
    'summary': summary
    'href': url
    }"""
    entries = []
    for entry_dict in current_feed_dict['entries']:
        entry = { 'headline': entry_dict['title'],
                  'summary': entry_dict['summary'],
                  'href': entry_dict['link'],
                  'date': "{}/{}/{} {}:{}:{}".format(entry_dict['published_parsed'].tm_mon,
                                                     entry_dict['published_parsed'].tm_mday,
                                                     entry_dict['published_parsed'].tm_year,
                                                     entry_dict['published_parsed'].tm_hour,
                                                     entry_dict['published_parsed'].tm_min,
                                                     entry_dict['published_parsed'].tm_sec)}
        entries.append(entry)

    return render_template('index.html', stories=entries)

@app.route('/json/', methods=['GET', 'POST'])
def json_root():
    return jsonify(current_feed_dict)

def update_news():
    global current_feed_dict
    while True:
        current_feed_dict = feedparser.parse('http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305')
        print "updating news"
        time.sleep(1800)

if __name__ == "__main__":

    thread.start_new_thread(update_news, ())
    app.run()
