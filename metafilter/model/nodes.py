from sqlalchemy import Table, Column, Integer, Unicode, ForeignKey, String, DateTime, Boolean, UniqueConstraint, Sequence, select, func
from sqlalchemy.orm import mapper, aliased
from sqlalchemy.sql import func, distinct
from sqlalchemy.exc import IntegrityError, DataError
from metafilter.model import metadata, uri_to_ltree, file_md5, uri_depth
from os.path import sep, isdir, basename
from datetime import datetime, timedelta
import re

import parsedatetime.parsedatetime as pdt
import parsedatetime.parsedatetime_consts as pdc

import logging

from metafilter.model import memoized

nodes_table = Table('node', metadata,
   Column('uri', Unicode, nullable=False, primary_key=True),
   Column('path', String),
   Column('md5', String(32)),
   Column('mimetype', String(32)),
   Column('created', DateTime),
   Column('updated', DateTime),
   Column('to_purge', Boolean, default=False),
   UniqueConstraint('uri', name='unique_uri')
)

TIME_PATTERN=re.compile(r'(\d{4}-\d{2}-\d{2})?(t)?(\d{4}-\d{2}-\d{2})?')
LOG = logging.getLogger(__name__)
PCONST = pdc.Constants()
CALENDAR = pdt.Calendar(PCONST)

@memoized
def by_uri(session, uri):
   qry = session.query(Node)
   qry = qry.filter( Node.uri == uri )
   return qry.first()

def update_nodes_from_path(sess, root, oldest_refresh=None):
   import os
   import mimetypes
   mimetypes.init()
   from os.path import isfile, join, abspath, sep

   root_ltree = uri_to_ltree(root)
   if not oldest_refresh:
      oldest_refresh = select([func.max(Node.updated)])
      oldest_refresh = oldest_refresh.where( Node.path.op("<@")(root_ltree) )
      oldest_refresh = oldest_refresh.execute().first()[0]

   LOG.info("Rescanning files that changed since %s" % oldest_refresh)

   for root, dirs, files in os.walk(root):

      # store folder nodes
      for node in root.split(sep):
         detached_file = Node(root)
         detached_file.mimetype = "other/directory"

         try:
            LOG.debug("Merging %s" % detached_file)
            attached_file = sess.merge(detached_file)
            sess.add(attached_file)
            LOG.debug("Added %s" % attached_file)
            sess.commit()
         except IntegrityError, exc:
            if exc.message == '(IntegrityError) duplicate key value violates unique constraint "node_path"\n':
               LOG.warning(exc.message)
               LOG.warning(exc.params)
               sess.rollback()
            else:
               raise
         except DataError, exc:
            if "(DataError) invalid byte sequence for encoding" in exc.message:
               LOG.warning(exc.message)
               LOG.warning(exc.params)
               sess.rollback()
            else:
               raise

      if 'Thumbs.db' in files:
         files.remove('Thumbs.db')

      scanned_files = 0
      for file in files:
         path = abspath(join(root, file))
         if not isfile(path):
            LOG.warning("Not a regular file: %r" % path)
            continue

         mod_time = max(
               datetime.fromtimestamp(os.stat(path).st_mtime),
               datetime.fromtimestamp(os.stat(path).st_ctime)
               )
         create_time = datetime.fromtimestamp(os.stat(path).st_ctime)

         # ignore files which have not been modified since last scan
         if oldest_refresh and mod_time < oldest_refresh:
            continue

         mimetype, _ = mimetypes.guess_type(path)

         detached_file = Node(path)
         #detached_file.md5 = file_md5(path)
         detached_file.mimetype = mimetype
         detached_file.created = create_time
         detached_file.updated = mod_time

         try:
            attached_file = sess.merge(detached_file)
            sess.add(attached_file)
            LOG.info("Added %s" % attached_file)
         except Exception, exc:
            LOG.error(str(exc))
         scanned_files += 1

      if scanned_files > 0:
         LOG.info("commit")
         sess.commit()

      if 'CVS' in dirs:
         dirs.remove('CVS')  # don't visit CVS directories

      if '.git' in dirs:
         dirs.remove('.git')  # don't visit CVS directories

      if '.svn' in dirs:
         dirs.remove('.svn')  # don't visit CVS directories

   sess.commit()

def get_children(sess, parent):
   qry = sess.query(Node)
   lquery = uri_to_ltree(parent) + ".*{1}"
   qry = qry.filter( Node.path.op("~")(lquery) )
   return qry.all()

def newer_than(sess, parent_uri=None, date=None):

   LOG.debug("Finding entries newer than %s in %r" % (date, parent_uri))

   if date == None:
      date = datetime.now()

   parent_path = uri_to_ltree(parent_uri)
   depth = uri_depth(parent_uri)

   stmt = sess.query(
         distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
         )
   stmt = stmt.filter(Node.created > date)
   stmt = stmt.filter( Node.path.op("<@")(parent_path) )
   stmt = stmt.subquery()
   qry = sess.query( Node )
   qry = qry.filter( Node.path.in_(stmt) )

   return qry

def older_than(sess, parent_uri=None, date=None):

   LOG.debug("Finding entries older than %s in %r" % (date, parent_uri))

   if date == None:
      date = datetime.now()

   parent_path = uri_to_ltree(parent_uri)
   depth = uri_depth(parent_uri)

   stmt = sess.query(
         distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
         )
   stmt = stmt.filter(Node.created < date)
   stmt = stmt.filter( Node.path.op("<@")(parent_path) )
   stmt = stmt.subquery()
   qry = sess.query( Node )
   qry = qry.filter( Node.path.in_(stmt) )
   qry = qry.order_by( func.subpath(Node.path, -1, 1) )

   return qry

def between(sess, parent_uri=None, start_date=None, end_date=None):

   LOG.debug("Finding entries between %s and %s in %r" % (start_date, end_date, parent_uri))

   if start_date == None:
      start_date = datetime.now() - timedelta(days=10)

   if end_date == None:
      end_date = datetime.now()

   parent_path = uri_to_ltree(parent_uri)
   depth = uri_depth(parent_uri)

   stmt = sess.query(
         distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
         )
   stmt = stmt.filter(Node.created.between(start_date, end_date))
   stmt = stmt.filter( Node.path.op("<@")(parent_path) )
   stmt = stmt.subquery()
   qry = sess.query( Node )
   qry = qry.filter( Node.path.in_(stmt) )

   return qry

def contains_text(sess, parent_uri=None, text=None):

   if text == None:
      text=""

   parent_path = uri_to_ltree(parent_uri)
   depth = uri_depth(parent_uri)

   stmt = sess.query(
         distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
         )
   stmt = stmt.filter(Node.uri.ilike(text))
   stmt = stmt.filter( Node.path.op("<@")(parent_path) )
   stmt = stmt.subquery()
   qry = sess.query( Node )
   qry = qry.filter( Node.path.in_(stmt) )

   return qry

@memoized
def from_query(sess, parent_uri, query):
   match = TIME_PATTERN.match(query)
   if  match and match.groups() != (None, None, None):
      groups = match.groups()
      if groups[0] and not groups[1] and not groups[2]:
         # matches 'yyyy-mm-dd'
         end_date = datetime.strptime(groups[0], "%Y-%m-%d")
         return older_than(sess, parent_uri, end_date)
      elif groups[0] and groups[1] == "t" and not groups[2]:
         # matches 'yyyy-mm-ddt'
         start_date = datetime.strptime(groups[0], "%Y-%m-%d")
         return newer_than(sess, parent_uri, start_date)
      elif not groups[0] and groups[1] == "t" and groups[2]:
         # matches 'tyyyy-mm-dd'
         end_date = datetime.strptime(groups[2], "%Y-%m-%d")
         return older_than(sess, parent_uri, end_date)
      elif groups[0] and groups[1] == "t" and groups[2]:
         # matches 'yyyy-mm-ddtyyyy-mm-dd'
         start_date = datetime.strptime(groups[0], "%Y-%m-%d")
         end_date = datetime.strptime(groups[2], "%Y-%m-%d")
         return between(sess, parent_uri, start_date, end_date)
      else:
         return []

   timetuple = CALENDAR.parse(query)
   start_date = datetime(*timetuple[0][0:6])
   return newer_than(sess, parent_uri, start_date)

   return []

class Node(object):

   def __init__(self, uri):
      self.path = uri_to_ltree(uri)
      self.uri = uri

   def __repr__(self):
      return "<Node %s %r>" % (
            self.is_dir() and "d" or "f",
            self.uri)

   def is_dir(self):
      return self.mimetype == "other/directory"

   @property
   def basename(self):
      return basename(self.uri)

mapper(Node, nodes_table)
