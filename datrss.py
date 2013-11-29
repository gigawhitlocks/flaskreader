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

newsfeeds = [
    ('Top Headlines', 'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305'),
    ('World', 'http://hosted2.ap.org/atom/APDEFAULT/cae69a7523db45408eeb2b3a98c0c9c5'),
    ('US National', 'http://hosted2.ap.org/atom/APDEFAULT/386c25518f464186bf7a2ac026580ce7'),
    ('Politics', 'http://hosted2.ap.org/atom/APDEFAULT/89ae8247abe8493fae24405546e9a1aa'),
    ('Business', 'http://hosted2.ap.org/atom/APDEFAULT/f70471f764144b2fab526d39972d37b3'),
    ('Technology', 'http://hosted2.ap.org/atom/APDEFAULT/495d344a0d10421e9baa8ee77029cfbd'),
    ('Sports', 'http://hosted2.ap.org/atom/APDEFAULT/347875155d53465d95cec892aeb06419'),
    ('Health', 'http://hosted2.ap.org/atom/APDEFAULT/bbd825583c8542898e6fa7d440b9febc'),
    ('Science', 'http://hosted2.ap.org/atom/APDEFAULT/b2f0ca3a594644ee9e50a8ec4ce2d6de'),
    ('Strange', 'http://hosted2.ap.org/atom/APDEFAULT/aa9398e6757a46fa93ed5dea7bd3729e')
]

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config.from_object(__name__)
app.current_feed_dicts = []

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

    content = {}
    for current_feed in app.current_feed_dicts:
        entries = []
        for entry_dict in current_feed[1]['entries']:
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

        content[current_feed[0]] = entries

    return render_template('index.html', stories=content)

@app.route('/json/', methods=['GET', 'POST'])
def json_root():
    return jsonify(app.current_feed_dicts)

def update_news():
    new_feed_dicts = []
    while True:
        for newsfeed in newsfeeds:
            new_feed_dicts.append((newsfeed[0], feedparser.parse(newsfeed[1])))
        print "updating news"
        app.current_feed_dicts = new_feed_dicts
        time.sleep(1800)

if __name__ == "__main__":

    thread.start_new_thread(update_news, ())
    app.run()
