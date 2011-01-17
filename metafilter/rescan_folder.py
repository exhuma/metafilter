#!/usr/bin/python
from metafilter.model import Session
import metafilter.model
from metafilter.model.nodes import update_nodes_from_path, remove_orphans
from datetime import datetime
import sys
from optparse import OptionParser

import logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def main():
   parser = OptionParser()
   parser.add_option("-d", "--dsn", dest="dsn",
                     help="Database DSN (see sqlalchemy docs for details)",
                     metavar="DSN")
   parser.add_option("-s", "--since", dest="since", default=None,
                     help="Only scan file that changed after this date (format: YYYY-MM-DD)")
   (options, args) = parser.parse_args()

   if not options.dsn:
      print >> sys.stderr, "The '-d/--dsn' option is required!"
      sys.exit(9)

   metafilter.model.set_dsn(options.dsn)

   if options.since:
      try:
         options.since = datetime.strptime(options.since, "%Y-%m-%d")
      except Exception, exc:
         LOG.error(exc)
         options.since = None


   sess = Session()
   update_nodes_from_path(sess, args[0], options.since)
   remove_orphans(sess, args[0])
   sess.close()

if __name__ == '__main__':
   main()

