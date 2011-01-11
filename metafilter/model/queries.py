from sqlalchemy import Table, Column, Integer, Unicode, ForeignKey, String, DateTime, Boolean, UniqueConstraint, Sequence
from sqlalchemy.orm import mapper, aliased
from sqlalchemy.sql import func, distinct
from metafilter.model import metadata, uri_to_ltree, Session, file_md5, uri_depth
from os.path import sep, isdir
from datetime import datetime, timedelta

import logging

from metafilter.model import memoized

query_table = Table('query', metadata,
   Column('query', String, nullable=False, primary_key=True),
)

LOG = logging.getLogger(__name__)

@memoized
def all(session):
   return session.query(Query).order_by(Query.query)

@memoized
def by_query(session, query):
   return session.query(Query).filter(Query.query == query).first()

class Query(object):

   def __init__(self, query):
      self.query = query

   def __repr__(self):
      return "<Query %r>" % (
            self.query)

mapper(Query, query_table)
