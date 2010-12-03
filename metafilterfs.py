#!/usr/bin/python

import fuse
import stat
import errno
from time import mktime
from model import Node, Query, Session
from model.nodes import from_query, TIME_PATTERN
from os.path import sep, join, exists
import os
import logging
import logging.handlers
import sys

fuse.fuse_python_api = (0, 2)

class LoggingFuse(fuse.Fuse):

    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.log = logging.getLogger(__name__)

    def getattr(self, path):
       self.log.debug("Called unimplemented getattr on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def getdir(self, path):
       self.log.debug("Called unimplemented getdir on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def mythread ( self ):
       self.log.debug("Called unimplemented mythread with %r" % locals())
       return -errno.ENOSYS

    def chmod ( self, path, mode ):
       self.log.debug("Called unimplemented chmod on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def chown ( self, path, uid, gid ):
       self.log.debug("Called unimplemented chown on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def fsync ( self, path, isFsyncFile ):
       self.log.debug("Called unimplemented fsync on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def link ( self, targetPath, linkPath ):
       self.log.debug("Called unimplemented link on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def mkdir ( self, path, mode ):
       self.log.debug("Called unimplemented mkdir on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def mknod ( self, path, mode, dev ):
       self.log.debug("Called unimplemented mknod on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def open ( self, path, flags ):
       self.log.debug("Called unimplemented open on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def read ( self, path, length, offset ):
       self.log.debug("Called unimplemented read on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def readlink ( self, path ):
       self.log.debug("Called unimplemented readlink on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def release ( self, path, flags ):
       self.log.debug("Called unimplemented release on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def rename ( self, oldPath, newPath ):
       self.log.debug("Called unimplemented rename on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def rmdir ( self, path ):
       self.log.debug("Called unimplemented rmdir on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def statfs ( self ):
       self.log.debug("Called unimplemented statfs on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def symlink ( self, targetPath, linkPath ):
       self.log.debug("Called unimplemented symlink on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def truncate ( self, path, size ):
       self.log.debug("Called unimplemented truncate on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def unlink ( self, path ):
       self.log.debug("Called unimplemented unlink on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def utime ( self, path, times ):
       self.log.debug("Called unimplemented utime on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def write ( self, path, buf, offset ):
       self.log.debug("Called unimplemented write on %s with %r" % (path, locals()))
       return -errno.ENOSYS

class MyStat(fuse.Stat):
   def __init__(self):
      self.st_mode = stat.S_IFDIR | 0755
      self.st_ino = 0
      self.st_dev = 0
      self.st_nlink = 2
      self.st_uid = 0
      self.st_gid = 0
      self.st_size = 4096
      self.st_atime = 0
      self.st_mtime = 0
      self.st_ctime = 0

class MetaFilterFS(LoggingFuse):

   def __init__(self, chroot, *args, **kwargs):
      fuse.Fuse.__init__(self, *args, **kwargs)
      self.log = logging.getLogger(__name__)
      self.setup_logging()
      self.log.info("*** Fuse Initialised")
      self.sess = Session()
      self.chroot = chroot

   def setup_logging(self):
      file_out = logging.handlers.RotatingFileHandler("/tmp/fuse.log", maxBytes=100000)
      formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
      file_out.setFormatter(formatter)
      self.log.addHandler(file_out)
      self.log.setLevel(logging.DEBUG)

   def abspath(self, relpath):
      node_path = self.path_items(relpath)
      out = join( self.chroot, *node_path[1:] )
      self.log.debug("Converted %s to %s" % ( relpath, out ))
      return out

   def depth(self, relpath):
      return len(self.path_items(relpath))

   def path_items(self, relpath):
      return relpath.split(sep)[1:]

   def getattr(self, path):
      if path.startswith('/.Trash'):
         return -errno.ENOENT

      self.log.debug("Retrieving stat for path %r => %s" % (path, self.path_items(path)))

      if path == "/":
         st = MyStat()
         return st

      try:
         if self.depth(path) == 1:
            node = self.sess.query(Query).filter(Query.query == self.path_items(path)[0]).first()
            if not node:
               return -errno.ENOENT
            self.log.debug("Node path of length 1 => %s" % self.path_items(path)[0])
            st = MyStat()
            return st
         elif self.depth(path) > 1:
            self.log.debug("Node path of length > 1 => query system stat")
            st = MyStat()
            abspath = self.abspath(path)
            if not exists(abspath):
               return -errno.ENOENT
            file_stat = os.stat(abspath)
            qry = self.sess.query(Node)
            qry = qry.filter( Node.uri == abspath )
            node = qry.first()
            if node:
               st.st_ctime = file_stat.st_ctime
               st.st_atime = file_stat.st_atime
               st.st_mtime = file_stat.st_mtime
               st.st_mode = file_stat.st_mode
               st.st_ino = file_stat.st_ino
               st.st_dev = file_stat.st_dev
               st.st_nlink = file_stat.st_nlink
               st.st_uid = file_stat.st_uid
               st.st_gid = file_stat.st_gid
               st.st_size = file_stat.st_size
            return st
         else:
            return -errno.ENOENT
      except Exception, ex:
         self.log.exception(ex)
      return -errno.ENOSYS

   def readdir(self, path, offset):
      self.log.debug("readdir %r with offset %r" % (path, offset))
      try:
         entries = [
               fuse.Direntry('.'),
               fuse.Direntry('..') ]
         if path == '/':
            # list the available queries first
            qry = self.sess.query(Query).order_by(Query.query)
            self.log.debug(qry)
            for row in qry:
               self.log.debug("Adding %s" % row)
               entries.append( fuse.Direntry(row.query.encode("utf8", "replace")) )
         else:
            nodes = path.split(sep)
            query = nodes[1]
            self.log.debug("query nodes: %s" % nodes)
            if len(nodes) == 2:
               parent_node = self.chroot
            else:
               parent_node = join(self.chroot, *nodes[2:])
            self.log.debug("Querying for %s in %s" % (query, parent_node))
            result = from_query( self.sess, parent_node, query )
            for row in result:
               entry = fuse.Direntry(row.basename.encode("utf8", "replace"))
               if row.is_dir():
                  entry.type = stat.S_IFDIR
               else:
                  entry.type = stat.S_IFREG
               entries.append(entry)
         for r in entries:
             self.log.debug("listing %r" % r)
             yield r
      except GeneratorExit:
         raise
      except Exception, ex:
         self.log.exception(ex)

   def rmdir(self, path):
      self.log.debug("* rmdir %s" % (path))
      leaf = path.split(sep)[-1]
      q = self.sess.query(Query).filter(Query.query == leaf).first()
      if not q:
         self.log.error("Query path %s does not exist!", path)
         return -errno.ENOENT
      try:
         self.sess.delete(q)
         self.sess.commit()
      except Exception, ex:
         self.log.exception(ex)
      return 0

   def mkdir(self, path, mode):
      self.log.debug("* mkdir %s %s" % (path, mode))
      leaf = path.split(sep)[-1]
      groups = TIME_PATTERN.match(leaf).groups()
      if groups == (None, None, None):
         self.log.error("Path %s is not a valid query expression!", path)
         return -errno.EINVAL
      q = Query(leaf)
      self.sess.add(q)
      self.sess.commit()
      return 0

   def read ( self, path, length, offset ):
      self.log.debug( '*** read %s - %s - %s' % (path, length, offset) )
      fptr = open( self.abspath(path), "rb" )
      fptr.seek(offset)
      chunk = fptr.read(length)
      return chunk

def main():
   usage="""MetaFilterFS: A filesystem which queries a DB to filter a tree based
on simple queries.""" + fuse.Fuse.fusage

   server = MetaFilterFS(
         chroot = sys.argv[1],
         version="%prog " + fuse.__version__,
         usage=usage,
         dash_s_do='setsingle')
   server.parser.add_option(
         mountopt="root",
         metavar="PATH",
         default='/',
         help="mount filtered filesystem from under PATH [default: %default]")
   server.parse(errex=1)
   server.main()

if __name__ == '__main__':
   main()

