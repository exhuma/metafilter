import logging

from sqlalchemy import Column, String
from metafilter.model import Base

from metafilter.model import memoized

LOG = logging.getLogger(__name__)


class Query(Base):

    __tablename__ = 'query'

    query = Column(String, nullable=False, primary_key=True)
    label = Column(String, nullable=True, default=None)

    @memoized
    @staticmethod
    def all(session):
        return session.query(Query).order_by(Query.query)

    @memoized
    @staticmethod
    def by_query(session, query):
        return session.query(Query).filter(Query.query == query).first()

    @staticmethod
    def update(session, old_query, new_query, label=None):
        upd = Query.__table__.update()
        upd = upd.values(query=new_query, label=label)
        upd = upd.where(Query.query == old_query)
        upd.execute()

    @staticmethod
    def delete(session, query):
        Query.__table__.delete(Query.query == query).execute()

    def __init__(self, query):
        self.query = query

    def __repr__(self):
        return "Query({!r})".format(self.query)
