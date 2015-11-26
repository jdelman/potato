# configs
import os

class Local(object):
  DEBUG = True
  SERVER_NAME = "localhost:8080"
  PREFERRED_URL_SCHEME = "http"
  MONGO_IP = "127.0.0.1"
  REDIS_IP = "127.0.0.1"
  APP_ROOT = os.path.dirname(os.path.abspath(__file__)) 


class Production(object):
  DEBUG = False
  SERVER_NAME = "jdelman.me"
  PREFERRED_URL_SCHEME = "https"
  MONGO_IP = "127.0.0.1"
  REDIS_IP = "127.0.0.1"
  APP_ROOT = os.path.dirname(os.path.abspath(__file__)) 