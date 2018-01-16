USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
# RUTOR_HOST = 'http://rus-tor.com'
RUTOR_HOST = 'http://www.xn--c1avfbif.net'
URL = '%s/browse/%%d/1/0/0' % RUTOR_HOST
TIMEOUT = 20
CONCURRENCY = 1
PAGES_COUNT = 10
DEBUG = True

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'rutor'

try:
    from config_local import *
except ImportError:
    pass

assert CONCURRENCY
assert PAGES_COUNT