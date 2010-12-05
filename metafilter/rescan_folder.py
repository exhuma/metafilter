#!/usr/bin/python
from metafilter.model import Session
import metafilter.model
from metafilter.model.nodes import update_nodes_from_path
import sys
from optparse import OptionParser

def main():
   parser = OptionParser()
   parser.add_option("-d", "--dsn", dest="dsn",
                     help="Database DSN (see sqlalchemy docs for details)",
                     metavar="DSN")
   (options, args) = parser.parse_args()

   import logging
   logging.basicConfig(level=logging.DEBUG)

   if not options.dsn:
      print >> sys.stderr, "The '-d/--dsn' option is required!"
      sys.exit(9)

   metafilter.model.set_dsn(options.dsn)

   sess = Session()
   update_nodes_from_path(sess, args[0])
   sess.close()

if __name__ == '__main__':
   main()

