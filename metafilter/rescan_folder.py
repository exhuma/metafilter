#!/usr/bin/python
from metafilter.model import Session
from metafilter.model.nodes import update_nodes_from_path
import sys

def main():
   sess = Session()
   update_nodes_from_path(sess, sys.argv[1])
   sess.close()

if __name__ == '__main__':
   main()

