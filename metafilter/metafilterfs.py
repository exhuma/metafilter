#!/usr/bin/python

import fuse
import stat
import errno
from time import mktime
import metafilter.model
from metafilter.model import Node, Query, Session
from metafilter.model.nodes import from_query, by_uri, TIME_PATTERN, from_incremental_query, map_to_fs
import metafilter.model.queries as queries
from os.path import sep, join, exists
import os
import logging
import logging.handlers
import sys
from datetime import datetime, timedelta

if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."
fuse.fuse_python_api = (0, 2)
fuse.feature_assert('stateful_files', 'has_init')
def path_items(relpath):
   return relpath.split(sep)[1:]

def flag2mode(flags):
   md = {os.O_RDONLY: 'r', os.O_WRONLY: 'w', os.O_RDWR: 'w+'}
   m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

   if flags | os.O_APPEND:
      m = m.replace('w', 'a', 1)

   return m

class LoggingFuseObsolete(fuse.Fuse):

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

    #def open ( self, path, flags ):
    #   self.log.debug("Called unimplemented open on %s with %r" % (path, locals()))
    #   return -errno.ENOSYS

    def read ( self, path, length, offset ):
       self.log.debug("Called unimplemented read on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def readlink ( self, path ):
       self.log.debug("Called unimplemented readlink on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def release ( self, *args ):
       self.log.debug("Called unimplemented release with %r" % (locals()))
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

    def link ( self, targetPath, linkPath ):
       self.log.debug("Called unimplemented link on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def mkdir ( self, path, mode ):
       self.log.debug("Called unimplemented mkdir on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def mknod ( self, path, mode, dev ):
       self.log.debug("Called unimplemented mknod on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def readlink ( self, path ):
       self.log.debug("Called unimplemented readlink on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def rename ( self, oldPath, newPath ):
       self.log.debug("Called unimplemented rename on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def rmdir ( self, path ):
       self.log.debug("Called unimplemented rmdir on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def statfs ( self ):
       self.log.debug("Called unimplemented statfs")
       return -errno.ENOSYS

    def symlink ( self, targetPath, linkPath ):
       self.log.debug("Called unimplemented symlink on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def unlink ( self, path ):
       self.log.debug("Called unimplemented unlink on %s with %r" % (path, locals()))
       return -errno.ENOSYS

    def utime ( self, path, times ):
       self.log.debug("Called unimplemented utime on %s with %r" % (path, locals()))
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

class MetaFile(object):

   def __init__(self, fs, path, flags, *mode):
      self.log = logging.getLogger("%s.%s" % (__name__, "MetaFile"))

      if '__flat__' in path:
         self.log.debug("Retrieving stat for flattened path %r" % (path))
         nodes = path.split(sep)
         md5name = nodes[-1]
         path = fs.map.get(md5name, None)
      else:
         # remove leading '/'
         path = path[1:]
         self.log.debug("Retrieving stat for path %r => %s" % (path, path_items(path)))
         path = map_to_fs(path)

      try:
         self.log.debug("Opening file at path %s in %s" % (path, os.getcwd()))
         self.file = os.fdopen(os.open(path, flags, *mode),
                               flag2mode(flags))
         self.fd = self.file.fileno()
         self.log.debug("Opened as %s" % self.file)
      except Exception, exc:
         self.log.exception(exc)

   def read(self, length, offset, *args):
      self.log.debug("Reading: %r" %locals() )
      self.file.seek(offset)
      return self.file.read(length)

   def write(self, buf, offset):
      self.file.seek(offset)
      self.file.write(buf)
      return len(buf)

   def release(self, *args):
      self.log.debug("Releasing: %r" %locals() )
      self.file.close()

   def _fflush(self):
      if 'w' in self.file.mode or 'a' in self.file.mode:
          self.file.flush()

   def fsync(self, isfsyncfile):
      self._fflush()
      if isfsyncfile and hasattr(os, 'fdatasync'):
          os.fdatasync(self.fd)
      else:
          os.fsync(self.fd)

   def flush(self):
      self._fflush()
      # cf. xmp_flush() in fusexmp_fh.c
      os.close(os.dup(self.fd))

   def fgetattr(self):
      try:
         return os.fstat(self.fd)
      except Exception, exc:
         self.log.exception(exc)

   def ftruncate(self, len):
      self.file.truncate(len)

   # def lock(self, cmd, owner, **kw):
   #    # The code here is much rather just a demonstration of the locking
   #    # API than something which actually was seen to be useful.

   #    # Advisory file locking is pretty messy in Unix, and the Python
   #    # interface to this doesn't make it better.
   #    # We can't do fcntl(2)/F_GETLK from Python in a platfrom independent
   #    # way. The following implementation *might* work under Linux. 
   #    #
   #    # if cmd == fcntl.F_GETLK:
   #    #     import struct
   #    # 
   #    #     lockdata = struct.pack('hhQQi', kw['l_type'], os.SEEK_SET,
   #    #                            kw['l_start'], kw['l_len'], kw['l_pid'])
   #    #     ld2 = fcntl.fcntl(self.fd, fcntl.F_GETLK, lockdata)
   #    #     flockfields = ('l_type', 'l_whence', 'l_start', 'l_len', 'l_pid')
   #    #     uld2 = struct.unpack('hhQQi', ld2)
   #    #     res = {}
   #    #     for i in xrange(len(uld2)):
   #    #          res[flockfields[i]] = uld2[i]
   #    #  
   #    #     return fuse.Flock(**res)

   #    # Convert fcntl-ish lock parameters to Python's weird
   #    # lockf(3)/flock(2) medley locking API...
   #    op = { fcntl.F_UNLCK : fcntl.LOCK_UN,
   #           fcntl.F_RDLCK : fcntl.LOCK_SH,
   #           fcntl.F_WRLCK : fcntl.LOCK_EX }[kw['l_type']]
   #    if cmd == fcntl.F_GETLK:
   #        return -EOPNOTSUPP
   #    elif cmd == fcntl.F_SETLK:
   #        if op != fcntl.LOCK_UN:
   #            op |= fcntl.LOCK_NB
   #    elif cmd == fcntl.F_SETLKW:
   #        pass
   #    else:
   #        return -EINVAL

   #    fcntl.lockf(self.fd, op, kw['l_start'], kw['l_len'])

class MetaFilterFS(LoggingFuse):

   def __init__(self, *args, **kwargs):
      fuse.Fuse.__init__(self, *args, **kwargs)
      self.log = logging.getLogger("metafilter")
      self.setup_logging()
      self.log.info("*** Fuse Initialised")
      self.sess = Session()
      self.root = '/'
      self.dsn = "sqlite://"
      self.map = {}

   def setup_logging(self):
      stdout = logging.StreamHandler()
      stdout.setLevel(logging.DEBUG)
      file_out = logging.handlers.RotatingFileHandler("/tmp/fuse.log", maxBytes=100000)
      formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
      file_out.setFormatter(formatter)
      stdout.setFormatter(formatter)
      self.log.addHandler(file_out)
      self.log.addHandler(stdout)
      self.log.setLevel(logging.DEBUG)

   def depth(self, relpath):
      return len(path_items(relpath))

   def fsinit(self):
      os.chdir(self.root)

   def getattr(self, path):
      if path.startswith('/.Trash'):
         return -errno.ENOENT

      if '__flat__' in path:
         self.log.debug("Retrieving stat for flattened path %r" % (path))
         nodes = path.split(sep)
         md5name = nodes[-1]
         fs_path = self.map.get(md5name, None)
      else:
         # remove leading '/'
         path = path[1:]
         self.log.debug("Retrieving stat for path %r => %s" % (path, path_items(path)))
         fs_path = map_to_fs(path)

      self.log.debug( 'Mapped %r to %r' % (path, fs_path) )

      try:
         if fs_path:
            self.log.debug("Node maps to filesystem => query system stat")
            st = MyStat()
            if not exists(fs_path):
               return -errno.ENOENT
            node = by_uri(self.sess, fs_path)
            if node:
               return os.lstat(fs_path)
            return st
         else:
            st = MyStat()
            return st
      except Exception, ex:
         self.log.exception(ex)
      return -errno.ENOSYS

   def readdir(self, path, offset):
      self.log.debug("readdir %r with offset %r" % (path, offset))

      self.map = {}

      # default (required) entries
      entries = [ fuse.Direntry('.'), fuse.Direntry('..') ]

      # remove leading '/'
      path = path[1:]

      # split into path elements
      for node in from_incremental_query(self.sess, path):
         if path.endswith('/__flat__'):
            entries.append(fuse.Direntry(node.md5name.encode(
               sys.getfilesystemencoding(), 'replace')))
            self.map[node.md5name] = node.uri
         else:
            entries.append(fuse.Direntry(node.basename.encode(
               sys.getfilesystemencoding(), 'replace')))

      # generate the output
      for r in entries:
         if not r.name:
            continue
         self.log.debug("listing %s" % r.name)
         yield r

   def readdir_old(self, path, offset):
      self.log.debug("readdir %r with offset %r" % (path, offset))
      try:
         entries = [
               fuse.Direntry('.'),
               fuse.Direntry('..') ]
         if path == '/':
            # list the available queries first
            for row in queries.all(self.sess):
               self.log.debug("Adding %s" % row)
               entries.append( fuse.Direntry(row.query.encode("utf8", "replace")) )
         else:
            nodes = path.split(sep)
            query = nodes[1]
            self.log.debug("query nodes: %s" % nodes)
            if len(nodes) == 2:
               parent_node = self.root
            else:
               parent_node = join(self.root, *nodes[2:])
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
            if not r.name:
               continue
            self.log.debug("listing %s" % r)
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
      #groups = TIME_PATTERN.match(leaf).groups()
      #if groups == (None, None, None):
      #   self.log.error("Path %s is not a valid query expression!", path)
      #   return -errno.EINVAL
      q = Query(leaf)
      self.sess.add(q)
      self.sess.commit()
      return 0

   # def read ( self, path, length, offset ):
   #    self.log.debug( '*** read %s - %s - %s' % (path, length, offset) )
   #    fptr = open( self.abspath(path), "rb" )
   #    fptr.seek(offset)
   #    chunk = fptr.read(length)
   #    return chunk

   def main(self, *a, **kw):

      class WrappedMetaFile(MetaFile):
         def __init__(self2, *args, **kwargs):
            MetaFile.__init__(self2, self, *args, **kwargs)

      self.file_class = WrappedMetaFile
      return fuse.Fuse.main(self, *a, **kw)

def main():
   usage="""MetaFilterFS:
      A filesystem which queries a DB to filter a tree based
   on simple queries.
   """ + fuse.Fuse.fusage

   server = MetaFilterFS(
         version="%prog " + fuse.__version__,
         usage=usage,
         dash_s_do='setsingle')
   server.parser.add_option(
         mountopt="root",
         metavar="PATH",
         default='/',
         help="mount filtered filesystem from under PATH [default: %default]")
   server.parser.add_option(
         mountopt="dsn",
         metavar="DSN",
         default='sqlite://',
         help="The database connection DSN. See sqlalchemy docs for it's format [default: %default]")
   server.parse(values=server, errex=1)

   metafilter.model.set_dsn(server.dsn)

   try:
      if server.fuse_args.mount_expected():
         os.chdir(server.root)
   except OSError:
      print >> sys.stderr, "can't enter root (%r) of underlying filesystem" % server.root
      sys.exit(1)

   server.main()

if __name__ == '__main__':
   main()

