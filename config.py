import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    IP_ADDRESS = os.environ.get('IP_ADDRESS')
