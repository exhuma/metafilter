#!/usr/bin/python
from __future__ import print_function
from datetime import datetime
from optparse import OptionParser
from os import makedirs
from os.path import expanduser, dirname, exists
import logging
import logging.handlers
import sys

from config_resolver import Config

LOG = logging.getLogger(__name__)
CONF = Config('wicked', 'metafilter')

from metafilter.model import Session, CONFIG, set_dsn
from metafilter.model.nodes import (
    calc_md5,
    remove_orphans,
    update_nodes_from_path,
)


def setup_logging(verbose=False, quiet=False):
    root_logger = logging.getLogger()
    LOG.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    if verbose:
        console_handler.setLevel(logging.DEBUG)

    if quiet:
        console_handler.setLevel(logging.WARNING)

    error_log = expanduser(CONFIG.get('cli_logging', 'error_log', None))
    if error_log:
        if not exists(dirname(error_log)):
            LOG.info('Creating logging folder: %s' % dirname(error_log))
            makedirs(dirname(error_log))
        error_handler = logging.handlers.RotatingFileHandler(
            filename=error_log, maxBytes=102400, backupCount=5)
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)


def parse_arguments():

    parser = OptionParser(usage='usage: %prog [options] <scan_folder>')
    parser.add_option(
        "-s", "--since",
        dest="since",
        default=None,
        help="Only scan file that changed after this date (format: YYYY-MM-DD)")
    parser.add_option(
        "-n", "--no-insert",
        dest="no_insert",
        default=False,
        action='store_true',
        help=("Do not insert or update new nodes. This may be usefule if you "
              "only want to remove old entries, or calculate the md5 sums"))
    parser.add_option(
        "-p", "--purge",
        dest="purge",
        default=False,
        action="store_true",
        help=("Remove orphans after scan. WARNING: this removes file not "
              "available on disk! If you work with removable devices, the "
              "device should be mounted and available before running this. "
              "Otherwise all files on from that device will be removed from "
              "the index!"))
    parser.add_option(
        "-m", "--md5",
        dest="md5",
        default=False,
        action="store_true",
        help=("Calculate md5sums after scan. This can take a long time, but is "
              "necessary to detect moves & duplictates"))
    parser.add_option(
        "-a", "--auto-tag-tail",
        dest="auto_tag_tail",
        default=False,
        action="store_true",
        help="Automatically add the 'leaf' folder-name to the tags")
    parser.add_option(
        "-w", "--auto-tag-word",
        dest="auto_tag_words",
        default=[],
        action="append",
        metavar="WORD",
        help=("If WORD appears anywhere as folder-name in the files path, add "
              "it to the tag list. This option can be specified as many times "
              "you want."))
    parser.add_option(
        "-v", "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="Verbose output to stdout")
    parser.add_option(
        "-q", "--quiet",
        dest="quiet",
        default=False,
        action="store_true",
        help="Suppresses informational messages from output (overrides -v)")
    parser.add_option(
        "-d", "--dsn",
        dest="dsn",
        default=CONF.get('database', 'dsn'),
        help="The database DSN")

    options, args = parser.parse_args()
    if not args:
        print(parser.print_usage(), file=sys.stderr)
        raise ValueError("No path specified!")

    return options, args


def main():

    try:
        options, args = parse_arguments()
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 9

    setup_logging(options.verbose, options.quiet)

    if options.dsn:
        set_dsn(options.dsn)
    else:
        LOG.fatal("No DSN specified!")
        return 9

    if options.since:
        try:
            options.since = datetime.strptime(options.since, "%Y-%m-%d")
        except Exception, exc:
            LOG.error(exc)
            options.since = None

    sess = Session()

    if not options.no_insert:
        update_nodes_from_path(sess, args[0], options.since,
                               options.auto_tag_tail, options.auto_tag_words)

    if options.purge:
        remove_orphans(sess, args[0])

    if options.md5:
        calc_md5(sess, args[0], options.since)

    sess.close()
    print("Rescan finished")
    return 0


if __name__ == '__main__':
    sys.exit(main())
