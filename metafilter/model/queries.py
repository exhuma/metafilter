import logging

from sqlalchemy import (
    Column,
    String,
    Table,
)
from sqlalchemy.orm import mapper
from metafilter.model import metadata

from metafilter.model import memoized

query_table = Table(
    'query', metadata,
    Column('query', String, nullable=False, primary_key=True),
    Column('label', String, nullable=True, default=None),
)

LOG = logging.getLogger(__name__)


@memoized
def all(session):
    return session.query(Query).order_by(Query.query)


@memoized
def by_query(session, query):
    return session.query(Query).filter(Query.query == query).first()


def update(session, old_query, new_query, label=None):
    upd = query_table.update()
    upd = upd.values(query=new_query, label=label)
    upd = upd.where(query_table.c.query == old_query)
    upd.execute()


def delete(session, query):
    query_table.delete(query_table.c.query == query).execute()


class Query(object):

    def __init__(self, query):
        self.query = query

    def __repr__(self):
        return "<Query %r>" % (
            self.query)

mapper(Query, query_table)
