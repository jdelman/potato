import os

from flask import Flask, request, send_from_directory
from redis import Redis
from rq import Queue

##

app = Flask(__name__)

config_name = os.environ.get('POTATO_CONFIG', 'Local')
app.config.from_object('potato.config.%s' % config_name)

from potato.tasks import add_video, make_feed_from_db

q = Queue(connection=Redis(app.config.get('REDIS_IP', '127.0.0.1')))


@app.route('/add_media')
def add_media():
  url = request.args.get('url')
  if not url:
    return 'You must specify the url parameter.'

  # run youtube-dl on that url
  q.enqueue(add_video, url)

  return 'Ok.'



@app.route('/feed')
def get_feed():
  content_type = 'application/rss+xml'
  return send_from_directory('static', 'potato.xml', mimetype=content_type)



@app.route('/rebuild_feed')
def rebuild_feed():
  q.enqueue(make_feed_from_db)
  return 'Rebuilding feed now...'