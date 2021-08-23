import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PjALA07lE1iFIP3heFAq'
    IP_ADDRESS = "192.168.0.12"
