from sqlalchemy import (
          Table,
          Column,
          Unicode,
          ForeignKey,
          select,
          desc,
          func,
          )
from sqlalchemy.orm import mapper, relation
from sqlalchemy.sql import distinct
from metafilter.model import metadata, uri_to_ltree, file_md5, uri_depth
from metafilter.model.queries import Query, query_table
from os.path import basename, exists
from datetime import datetime
import re
from sys import getfilesystemencoding

import parsedatetime.parsedatetime as pdt
import parsedatetime.parsedatetime_consts as pdc

import logging

from metafilter.model import memoized

# --- Table definitions ------------------------------------------------------

tag_table = Table('tag', metadata,
    Column('name', Unicode, nullable=False, primary_key=True),
)

tag_in_tag_group_table = Table('tag_in_tag_group', metadata,
    Column('tagname', Unicode, ForeignKey('tag.name', onupdate="CASCADE", ondelete='CASCADE'), nullable=False, primary_key=True),
    Column('groupname', Unicode, ForeignKey('tag_group.name', onupdate="CASCADE", ondelete='CASCADE'), nullable=False, primary_key=True),
)

node_has_tag_table = Table('node_has_tag', metadata,
    Column('uri', Unicode, ForeignKey('node.uri'), nullable=False, primary_key=True),
    Column('tag', Unicode, ForeignKey('tag.name'), nullable=False, primary_key=True),
)

# --- "Static" methods -------------------------------------------------------

def tag_counts(sess):
    tags = select([node_has_tag_table.c.tag, func.count().label('count')])
    tags = tags.order_by(desc('count'))
    tags = tags.group_by(node_has_tag_table.c.tag)
    return tags

# --- Entity Classes ---------------------------------------------------------

class Tag(object):

    @classmethod
    def find(self, sess, name):
        qry = sess.query(Tag)
        qry = qry.filter( Tag.name == name )
        return qry.first()

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

# --- Mappers ----------------------------------------------------------------

mapper(Tag, tag_table)

