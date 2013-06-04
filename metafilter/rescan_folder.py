#!/usr/bin/python
from os.path import expanduser, dirname, exists
from os import makedirs
import sys
from datetime import datetime
from optparse import OptionParser
import logging
import logging.handlers

from config_resolver import Config

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.INFO)
CONSOLE_HANDLER.setFormatter(FORMATTER)
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(CONSOLE_HANDLER)

CONF = Config('wicked', 'metafilter')

from metafilter.model import Session, CONFIG, set_dsn
from metafilter.model.nodes import update_nodes_from_path, remove_orphans, calc_md5

error_log = expanduser(CONFIG.get('cli_logging', 'error_log', None))
if error_log:
    if not exists(dirname(error_log)):
        LOG.info('Creating logging folder: %s' % dirname(error_log))
        makedirs(dirname(error_log))
    ERROR_HANDLER = logging.handlers.RotatingFileHandler(filename=error_log, maxBytes=102400, backupCount=5)
    ERROR_HANDLER.setLevel(logging.WARNING)
    ERROR_HANDLER.setFormatter(FORMATTER)
    logging.getLogger().addHandler(ERROR_HANDLER)

def main():
    parser = OptionParser(usage='usage: %prog [options] <scan_folder>')
    parser.add_option("-s", "--since", dest="since", default=None,
                            help="Only scan file that changed after this date (format: YYYY-MM-DD)")
    parser.add_option("-n", "--no-insert", dest="no_insert", default=False, action='store_true',
                            help="Do not insert or update new nodes. This may be usefule if you only want to remove old entries, or calculate the md5 sums")
    parser.add_option("-p", "--purge", dest="purge", default=False, action="store_true",
                help="Remove orphans after scan. WARNING: this removes file not available on disk! If you work with removable devices, the device should be mounted and available before running this. Otherwise all files on from that device will be removed from the index!")
    parser.add_option("-m", "--md5", dest="md5", default=False, action="store_true",
                help="Calculate md5sums after scan. This can take a long time, but is necessary to detect moves & duplictates")
    parser.add_option("-a", "--auto-tag-tail", dest="auto_tag_tail", default=False, action="store_true",
                help="Automatically add the 'leaf' folder-name to the tags")
    parser.add_option("-w", "--auto-tag-word", dest="auto_tag_words", default=[], action="append", metavar="WORD",
                help="If WORD appears anywhere as folder-name in the files path, add it to the tag list. This option can be specified as many times you want.")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true",
                help="Verbose output to stdout")
    parser.add_option("-q", "--quiet", dest="quiet", default=False, action="store_true",
                help="Suppresses informational messages from output (overrides -v)")
    parser.add_option("-d", "--dsn", dest="dsn",
                      help="The database DSN", default="")

    (options, args) = parser.parse_args()

    if options.verbose:
        CONSOLE_HANDLER.setLevel(logging.DEBUG)
    if options.quiet:
        CONSOLE_HANDLER.setLevel(logging.WARNING)

    if options.dsn:
        set_dsn(options.dsn)
    else:
        print LOG.fatal("No DSN specified!")
        return 9

    if options.since:
        try:
            options.since = datetime.strptime(options.since, "%Y-%m-%d")
        except Exception, exc:
            LOG.error(exc)
            options.since = None

    if not args:
        LOG.critical("No path specified!")
        print parser.print_usage()
        sys.exit(9)

    sess = Session()

    if not options.no_insert:
        update_nodes_from_path(sess, args[0], options.since,
                options.auto_tag_tail, options.auto_tag_words)

    if options.purge:
        remove_orphans(sess, args[0])

    if options.md5:
        calc_md5(sess, args[0], options.since)

    sess.close()
    print "Rescan finished"

if __name__ == '__main__':
    main()

