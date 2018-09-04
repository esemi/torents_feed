USER_AGENT = 'rutor.esemi.ru Bot v0.2'
RUTOR_HOST = 'http://new-rutor.org'  # fixme
URL = '%s/browse/%%d/1/0/0' % RUTOR_HOST
TIMEOUT = 20
CONCURRENCY = 1
PAGES_COUNT = 2
DEBUG = False

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'rutor'

LIMIT_MAX = 1000

try:
    from config_local import *
except ImportError:
    pass


CONCURRENCY = min(CONCURRENCY, PAGES_COUNT)

assert CONCURRENCY
assert PAGES_COUNT
