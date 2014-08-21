from os.path import split
import logging
import os


LOG = logging.getLogger(__name__)


def splitpath(path):
    """
    Split path into all it's elements. Not only head/tail.
    """
    output = []
    while os.sep in path and path != os.sep:
        head, tail = split(path)
        output.insert(0, tail)
        path = head
    return output
