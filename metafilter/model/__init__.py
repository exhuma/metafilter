import functools
import logging

from datetime import datetime, timedelta
from hashlib import md5
from os.path import sep
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import re
import sqlalchemy
import sqlalchemy.types as types

NON_LTREE = re.compile(r'[^a-zA-Z0-9/]')
LOG = logging.getLogger(__name__)
Base = declarative_base()


class LTree(types.UserDefinedType):
    "LTree Type for PostgreSQL."

    def get_col_spec(self):
        return "ltree"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            return str(value)
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            return str(value)
        return process



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
            LOG.debug("Removing obsolete value "
                      "for args %r from cache." % (args,))
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


def make_scoped_session(dsn):
    engine = create_engine(dsn)
    return scoped_session(sessionmaker(bind=engine))


from metafilter.model.nodes import Node  # NOQA
from metafilter.model.queries import Query  # NOQA
from metafilter.model.tags import Tag  # NOQA
