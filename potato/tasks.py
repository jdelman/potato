import os
import json
import subprocess
import string
from datetime import datetime

from potato import app as potato_app

import pytz
from flask import url_for
from feedgen.feed import FeedGenerator
from pymongo import MongoClient

###

ip = potato_app.config.get('MONGO_IP', '127.0.0.1')
print 'using mongo_ip: %s' % ip
mc = MongoClient(ip)
db = mc.potato


def setup_feed():
  fg = FeedGenerator()

  fg.load_extension('podcast')

  fg.language('en')
  fg.id('https://jdelman.me/potato')
  fg.author(name='Potato', email='joshdelman@gmail.com')
  fg.link(href='https://jdelman.me/potato', rel='alternate')
  fg.logo('https://jdelman.me/static/potato.jpg')
  fg.title("Potato - Josh's Saved Videos")
  fg.subtitle("Automatically generated RSS.")

  return fg


def add_video(url):
  print 'Received add_video task for URL: %s' % url

  # get title & description of the video
  metadata_output = subprocess.check_output(
    ['youtube-dl', '--get-title', '--get-description',
     '--dump-json', url])

  title, desc, json_data = metadata_output.splitlines()

  try:
    json_data = json.loads(json_data)
  except:
    json_data = None

  if json_data:
    author = json_data.get('uploader', 'J. Delman')
    url = json_data.get('webpage_url', url)


  filename_rel = make_legal_filename(title) + '.mp3'
  filename_abs = os.path.join(potato_app.config.get('APP_ROOT'),
    'static', 'media', filename_rel)

  # download the file & convert to mp3
  audio = subprocess.check_output(
    ['youtube-dl', '-x', '--audio-format=mp3', '--embed-thumbnail',
     '-o', filename_abs, url])

  # TODO: check to ensure the file downloaded properly

  # get file size
  size = os.path.getsize(filename_abs)

  # add to db
  item = {
    'title': title,
    'pubdate': datetime.utcnow(),
    'guid': url,
    'description': desc,
    'author': author,
    'size': size,
    'local_filename': filename_rel
  }
  db.files.update(
    {'local_filename': filename_rel},
    {'$set': item},
    upsert=True
  )

  print 'Video file "%s" inserted into database. Rebuilding feed...' % title

  # remake RSS feed
  make_feed_from_db()

  print 'Done.'


def make_feed_from_db():
  fg = setup_feed()

  files = db.files.find()

  for f in files:
    # create an entry
    print 'Adding entry for %s...' % f['local_filename']

    fe = fg.add_entry()
    fe.id(f['guid'])
    fe.link(href=f['guid'], rel='alternate')
    fe.title(f['title'])
    fe.pubdate(f['pubdate'].replace(tzinfo=pytz.UTC))
    fe.description(f['description'])
    # fe.author(f['author'])

    # may want to change this to hardcoded
    with potato_app.app_context():
      fe.enclosure(
        url_for('static', filename='media/%s' % f['local_filename']),
        unicode(f['size']),
        'audio/mpeg'
      )

  potato_output_filename = os.path.join(potato_app.config.get('APP_ROOT'),
    'static', 'potato.xml')
  fg.rss_file(potato_output_filename)

  print 'Done generating feed.'


def make_legal_filename(filename):
  safechars = '_-.()' + string.digits + string.ascii_letters
  return ''.join([x for x in filename if x in safechars])



if __name__ == "__main__":
  make_mp3_from_url('http://blog.pyston.org/2015/11/24/pyston-talk-recording/')