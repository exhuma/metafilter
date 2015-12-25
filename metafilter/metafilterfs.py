#!/usr/bin/env python

from collections import defaultdict
from errno import ENOENT, ENOSYS
from logging import handlers
from os.path import exists
from stat import S_IFDIR
from sys import argv, exit
from time import time
import logging
import os
import sys

from fuse import FUSE, Operations, FuseOSError
from config_resolver import Config

from metafilter.model import make_scoped_session, memoized, Node
from metafilter.model.nodes import subdirs


LOG = logging.getLogger(__name__)
CONF = Config('wicked', 'metafilter')


class MetaFilterFs(Operations):
    def __init__(self, session, root):
        self.files = {}  # TODO remove
        self.data = defaultdict(str)  # TODO remove
        self.fd = 0  # TODO remove
        now = time()
        self.files['/'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)

        self.log = logging.getLogger(__name__)
        self.setup_logging()
        self.log.info("*** Fuse Initialised")
        self.sess = session
        self.root = '/'

        try:
            os.chdir(root)
        except OSError:
            print >> sys.stderr, ("can't enter root (%r) of underlying "
                                  "filesystem") % root
            sys.exit(1)

    def setup_logging(self):
        stdout = logging.StreamHandler()
        stdout.setLevel(logging.DEBUG)
        file_out = handlers.RotatingFileHandler(
            "/tmp/fuse.log", maxBytes=100000)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_out.setFormatter(formatter)
        stdout.setFormatter(formatter)
        self.log.addHandler(file_out)
        self.log.addHandler(stdout)
        self.log.setLevel(logging.DEBUG)

    def getattr(self, path, fh=None):
        self.log.debug("Entering getattr. Locals: %r" % locals())

        if path.startswith('/.Trash'):
            raise FuseOSError(ENOENT)

        if path != "/":
            fs_path = map_to_fs(self.sess, path)
        else:
            fs_path = None

        self.log.debug('Mapped %r to %r' % (path, fs_path))

        try:
            if fs_path:
                self.log.debug("Node maps to filesystem => query system stat")
                if not exists(fs_path):
                    raise FuseOSError(ENOENT)
                node = by_uri(self.sess, fs_path)
                if node:
                    stat = os.lstat(fs_path)
                    return dict((key, getattr(stat, key))
                                for key in ('st_atime', 'st_ctime',
                                            'st_gid', 'st_mode', 'st_mtime',
                                            'st_nlink', 'st_size', 'st_uid'))
                return dict(
                    st_mode=(S_IFDIR | 0755),
                    st_ctime=time(),
                    st_mtime=time(),
                    st_atime=time(),
                    st_nlink=2
                )
            else:
                return dict(
                    st_mode=(S_IFDIR | 0755),
                    st_ctime=time(),
                    st_mtime=time(),
                    st_atime=time(),
                    st_nlink=2
                )
        except Exception, ex:
            self.log.exception(ex)
        raise FuseOSError(ENOSYS)

    def read(self, path, size, offset, fh):
        self.log.debug("Entering read. Locals: %r" % locals())
        fs_path = map_to_fs(self.sess, path)
        self.log.info('Reading local file %r' % fs_path)
        fptr = open(fs_path)
        fptr.seek(offset, 0)
        data = fptr.read(size)
        fptr.close()
        return data

    @memoized
    def readdir(self, path, fh):
        self.log.info("*** readdir %r with fh %r" % (path, fh))

        # default (required) entries
        entries = ['.', '..']

        # remove leading '/'
        path = path[1:]

        # retrieve subfolders
        for node in subdirs(self.sess, path):
            entries.append(node.basename.encode(
                sys.getfilesystemencoding(), 'replace'))

        # split into path elements
        for node in from_incremental_query(self.sess, path):
            if path.endswith('/__flat__'):
                entries.append(node.flatname.encode(
                    sys.getfilesystemencoding(), 'replace'))
            else:
                entries.append(node.basename.encode(
                    sys.getfilesystemencoding(), 'replace'))
        return entries


if __name__ == "__main__":
    dsn = CONF.get('database', 'dsn')
    if len(argv) != 3:
        print 'usage: %s <root> <mountpoint>' % argv[0]
        exit(1)
    FUSE(MetaFilterFs(make_scoped_session(dsn), argv[1]),
         argv[2],
         foreground=True,
         allow_other=True)
