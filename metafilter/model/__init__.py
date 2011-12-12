from ConfigParser import SafeConfigParser
from cStringIO import StringIO

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from os.path import sep
from hashlib import md5
from datetime import datetime, timedelta
import re

import logging
import functools

NON_LTREE = re.compile(r'[^a-zA-Z0-9/]')
LOG = logging.getLogger(__name__)
CONFIG = None
metadata = MetaData()
Session = sessionmaker()

def loadconfig(filename):

    defaults=StringIO("""\
[cli_logging]
error_log=
""")

    config = SafeConfigParser()
    config.readfp(defaults)
    config.read(filename)

    dsn = config.get('database', 'dsn', None)
    if not dsn:
        raise ValueError('No DSN found in the config file! This is required!')

    set_dsn(dsn)
    return config

class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        obsoletion = datetime.now() - timedelta(seconds=60*5)
        if args in self.cache and self.cache[args][1] < obsoletion:
            # value too old. Remove it from the cache
            LOG.debug("Removing obsolete value for args %r from cache." % (args,))
            del(self.cache[args])

        try:
            output = self.cache[args][0]
            LOG.debug("Cache hit for args %r." % (args,))
            return output
        except KeyError:
            LOG.debug("Initialising cache for args %r." % (args,))
            value = self.func(*args)
            if isinstance(value, sqlalchemy.orm.query.Query):
                result = value.all()
                self.cache[args] = (result, datetime.now())
                return result
            else:
                self.cache[args] = (value, datetime.now())
                return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            LOG.warning("Uncachable function call for args %r" % (args,))
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

def uri_depth(uri):
    "determines the depth of a uri"
    if not uri:
        return 0
    if uri.endswith(sep):
        uri = uri[0:-1]
    return len(uri.split(sep))

def file_md5(path):
    """
    Return the MD5 hash of the file
    """
    hash = md5()
    fptr = open(path, "rb")
    chunk = fptr.read(1024)
    while chunk:
        hash.update(chunk)
        chunk = fptr.read(1024)
    fptr.close()
    return hash.hexdigest()

def uri_to_ltree(uri):
    if not uri or uri == "/":
        return "ROOT"

    if uri.endswith(sep):
        uri = uri[0:-1]

    if uri.startswith(sep):
        ltree = "ROOT%s%s" % (sep, uri[1:])
    else:
        ltree = uri

    # the ltree module uses "." as path separator. Replace dots by
    # underscores and path separators by dots
    ltree = NON_LTREE.sub("_", ltree)
    ltree = ltree.replace(sep, ".")
    return ltree

def set_dsn(dsn):
    engine = create_engine(dsn)
    metadata.bind = engine
    Session.bind = engine

from metafilter.model.nodes import Node
from metafilter.model.queries import Query
from metafilter.model.tags import Tag

#
# Parse the config file
#
from os.path import join, exists, expanduser
from os import getcwd

paths = [
    join(getcwd(), 'config.ini'),
    join(expanduser("~"), '.metafilter', 'config.ini'),
    join('/', 'etc', 'metafilter', 'config.ini'),
]

for path in paths:
    if not exists(path):
        continue
    LOG.debug('Reading config from %s' % path)
    CONFIG = loadconfig(path)

if not CONFIG:
    LOG.error('Unable to open config file (search order: %s)' % (', '.join(paths)))
