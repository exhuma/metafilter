from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from os.path import sep
from hashlib import md5
import re

NON_LTREE = re.compile(r'[^a-zA-Z0-9/]')
metadata = MetaData()
Session = sessionmaker()

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
   if not uri or uri=="/":
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

