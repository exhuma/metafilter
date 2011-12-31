#-*- coding: utf-8 -*-
from os import putenv
import unittest2 as unittest
from metafilter.model import Node
from metafilter.model import Session, CONFIG

def setUpModule():
    from subprocess import call
    import logging
    logging.basicConfig(level=logging.DEBUG)
    print "loading DDL scripts..."
    call(['psql', '--cluster', '8.4/main', '-q', '-U', 'postgres', '-f', 'db/clean.sql', 'metafilter_hstore'])
    call(['psql', '--cluster', '8.4/main', '-q', '-U', 'postgres', '-f', '/usr/share/postgresql/8.4/contrib/ltree.sql', 'metafilter_hstore'])
    call(['psql', '--cluster', '8.4/main', '-q', '-U', 'postgres', '-f', '/usr/share/postgresql/8.4/contrib/hstore.sql', 'metafilter_hstore'])
    call(['psql', '--cluster', '8.4/main', '-q', '-U', 'postgres', '-f', 'db/create.sql', 'metafilter_hstore'])
    print "Done! Database re-initialised"

class TestModel(unittest.TestCase):
    """
    Testing the model on the folder "testdata". It must exist!
    """

    # testdata/
    # ├── images
    # │   └── Crystal_Clear_action_filenew.png
    # └── setup.py

    def setUp(self):
        self.sess = Session()

    def tearDown(self):
        self.sess.close()

    def test_rescan(self):
        Node.scan_path(self.sess, 'testdata')

        print 1

if __name__ == '__main__':
    unittest.main()
