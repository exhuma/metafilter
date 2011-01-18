from sqlalchemy import Table, Column, Integer, Unicode, ForeignKey, String, DateTime, Boolean, UniqueConstraint, Sequence, select, func, update
from sqlalchemy.orm import mapper, aliased
from sqlalchemy.sql import func, distinct
from sqlalchemy.exc import IntegrityError, DataError
from metafilter.model import metadata, uri_to_ltree, file_md5, uri_depth
from metafilter.model.queries import Query, query_table
from os.path import sep, isdir, basename, exists
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
   Column('rating', Integer, default=0),
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

def by_path(session, path):
   qry = session.query(Node)
   qry = qry.filter( Node.path == path )
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

def remove_orphans(sess, root):
   root_ltree = uri_to_ltree(root)
   qry = select([Node.uri])
   qry = qry.where( Node.path.op("<@")(root_ltree) )
   for row in qry.execute():
      if not exists(row[0]):
         LOG.info('Removing orphan %r' % row[0])
         try:
            nodes_table.delete(nodes_table.c.uri == row[0]).execute()
            sess.commit()
         except:
            sess.rollback()

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

def rated(sess, nodes, flatten=False):

   query_string = 'rating/%s' % str.join('/', nodes)

   if not nodes or len(nodes) < 2:
      # no details known yet. Find appropriate queries
      output = []
      stmt = sess.query(Query.query)
      LOG.debug('Listing nodes starting with %r' % query_string)
      stmt = stmt.filter(query_table.c.query.startswith(query_string))
      stmt = stmt.order_by(query_table.c.query)
      for row in stmt:
         sub_nodes = row.query.split('/')
         # we're in the case where the initial nodes were empty. We only return
         # the next element
         output.append(DummyNode(sub_nodes[len(nodes)+1]))
      return output

   op = nodes.pop(0)
   value = int(nodes.pop(0))
   parent_uri = '/'.join(nodes)

   LOG.debug("Finding entries rated %s %2d in %s" % (op, value, parent_uri))

   parent_path = uri_to_ltree(parent_uri)
   depth = uri_depth(parent_uri)

   if flatten:
      stmt = sess.query(Node)
   else:
      stmt = sess.query(
            distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
            )

   if op == 'gt':
      stmt = stmt.filter(Node.rating > value)
   elif op == 'ge':
      stmt = stmt.filter(Node.rating >= value)
   elif op == 'lt':
      stmt = stmt.filter(Node.rating < value)
   elif op == 'le':
      stmt = stmt.filter(Node.rating <= value)
   elif op == 'eq':
      stmt = stmt.filter(Node.rating == value)
   elif op == 'ne':
      stmt = stmt.filter(Node.rating != value)

   stmt = stmt.filter( Node.path.op("<@")(parent_path) )

   if not flatten:
      stmt = stmt.subquery()
      qry = sess.query( Node )
      qry = qry.filter( Node.path.in_(stmt) )
      return qry

   return stmt

def all(sess, nodes, flatten=False):

   parent_uri = '/'.join(nodes)

   parent_path = uri_to_ltree(parent_uri)
   depth = uri_depth(parent_uri)

   stmt = sess.query(
         distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
         )

   stmt = stmt.filter( Node.path.op("<@")(parent_path) )
   stmt = stmt.subquery()
   qry = sess.query( Node )
   qry = qry.filter( Node.path.in_(stmt) )

   return qry

def dated(sess, nodes, flatten=False):

   query_string = 'date/%s' % str.join('/', nodes)

   if not nodes or len(nodes) < 1:
      # no details known yet. Find appropriate queries
      output = []
      stmt = sess.query(Query.query)
      LOG.debug('Listing nodes starting with %r' % query_string)
      stmt = stmt.filter(query_table.c.query.startswith(query_string))
      stmt = stmt.order_by(query_table.c.query)
      for row in stmt:
         sub_nodes = row.query.split('/')
         # we're in the case where the initial nodes were empty. We only return
         # the next element
         output.append(DummyNode(sub_nodes[len(nodes)+1]))
      return output

   date_string = nodes.pop(0)
   parent_uri = '/'.join(nodes)

   LOG.debug("Finding entries using date string %s" % (date_string))

   match = TIME_PATTERN.match(date_string)
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

   timetuple = CALENDAR.parse(date_string)
   start_date = datetime(*timetuple[0][0:6])
   return newer_than(sess, parent_uri, start_date)

def rated_old(sess, parent_uri, op, value):

   LOG.debug("Finding entries rated %s %2d in %s" % (op, value, parent_uri))

   parent_path = uri_to_ltree(parent_uri)
   depth = uri_depth(parent_uri)

   stmt = sess.query(
         distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
         )

   if op == 'gt':
      stmt = stmt.filter(Node.rating > value)
   elif op == 'ge':
      stmt = stmt.filter(Node.rating >= value)
   elif op == 'lt':
      stmt = stmt.filter(Node.rating < value)
   elif op == 'le':
      stmt = stmt.filter(Node.rating <= value)
   elif op == 'eq':
      stmt = stmt.filter(Node.rating == value)
   elif op == 'ne':
      stmt = stmt.filter(Node.rating != value)

   stmt = stmt.filter( Node.path.op("<@")(parent_path) )
   stmt = stmt.subquery()
   qry = sess.query( Node )
   qry = qry.filter( Node.path.in_(stmt) )

   return qry

def set_rating(path, value):
   upd = nodes_table.update()
   upd = upd.values(rating=value)
   upd = upd.where(nodes_table.c.path==path)
   upd.execute()

def from_incremental_query(sess, query):
   LOG.debug('parsing incremental query %r' % query)

   if not query or query == 'root' or query == '/':
      # list the available query schemes
      return [
            DummyNode('rating'),
            DummyNode('date'),
            DummyNode('all'),
            ]
   else:
      if query.startswith('root'):
         query = query[5:]
      query_nodes = query.split('/')

   LOG.debug('Query nodes: %r' % query_nodes)

   query_type = query_nodes.pop(0).lower()
   if query_nodes and query_nodes[-1] == "__flat__":
      query_nodes.pop()
      flatten = True
   else:
      flatten = False

   if query_type == 'rating':
      return rated(sess, query_nodes, flatten)
   elif query_type == 'date':
      return dated(sess, query_nodes, flatten)
   elif query_type == 'all':
      return all(sess, query_nodes, flatten)

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

def from_query2(sess, query_path):
   query_nodes = query_path.split('/')
   query_type = query_nodes.pop(0)

   if query_type == 'date':
      query = query_nodes.pop(0)
      parent_uri = '/'.join(query_nodes)
      return from_query(sess, "/%s"%parent_uri, query)

   elif query_type == 'rating':
      op = query_nodes.pop(0)
      value = int(query_nodes.pop(0))
      parent_uri = '/'.join(query_nodes)
      return rated(sess, "/%s"%parent_uri, op, value)

def map_to_fs(query):
   """
   Remove any query specific elements, leaving only the fs-path
   """
   LOG.debug('Mapping to FS %r' % query)
   query_nodes = query.split("/")

   if not query_nodes:
      return None

   query_type = query_nodes.pop(0)

   if query_type == 'rating':
      if len(query_nodes) > 2:
         op = query_nodes.pop(0)
         value = query_nodes.pop(0)
         if query_nodes:
            query_nodes.pop(0) # remove leading 'ROOT'
         return '/' + '/'.join(query_nodes)

   elif query_type == 'date':
      if len(query_nodes) > 1:
         date_string = query_nodes.pop(0)
         if query_nodes:
            query_nodes.pop(0) # remove leading 'ROOT'
         return '/' + '/'.join(query_nodes)

   return None

class DummyNode(object):

   def __init__(self, label):
      self.label = label

   def __repr__(self):
      return "<DummyNode %s %r>" % (
            self.is_dir() and "d" or "f",
            self.label)

   def is_dir(self):
      return True

   @property
   def basename(self):
      return self.label

class Node(DummyNode):

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
      if self.uri == '/':
         return 'ROOT'
      return basename(self.uri)

   @property
   def md5name(self):
      from hashlib import md5
      if self.uri == '/':
         return 'ROOT'

      extension_parts = self.uri.rsplit('.', 1)
      if len(extension_parts) > 1:
         ext = extension_parts[-1]
      else:
         ext = ""

      out = "%s.%s" % (md5(self.uri).hexdigest(), ext)
      return out

mapper(Node, nodes_table)
