from datetime import datetime
from os.path import basename, exists, dirname, split, join, abspath
from sys import getfilesystemencoding
import logging
import os
import re

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Unicode,
    bindparam,
    func,
    not_,
    or_,
    select,
    text,
)

from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relation
from sqlalchemy.sql import distinct, cast
import parsedatetime.parsedatetime as pdt

from metafilter.util import splitpath
from metafilter.model import memoized
from metafilter.model import Base, uri_to_ltree, file_md5, uri_depth
from metafilter.model.queries import Query
from metafilter.model.tags import (
    Tag,
    node_has_tag_table,
    tag_in_tag_group_table
)

TIME_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2})?(t)?(\d{4}-\d{2}-\d{2})?')
LOG = logging.getLogger(__name__)
CALENDAR = pdt.Calendar()

# folder names must be longer than this to be auto-tagged
TAIL_DIR_THRESHOLD = 3


def subdirs(sess, query):
    LOG.debug('subfolders in %s' % query)

    if not query or query == 'root' or query == '/':
        return []
        # handled by from incremental_query
    else:
        if query.startswith('root'):
            query = query[5:]
        query_nodes = query.split('/')

    LOG.debug('Query nodes: %r' % query_nodes)

    # pop the query type off the beginning
    query_types = query_nodes.pop(0).lower()
    query_types = [x.strip() for x in query_types.split(',')]

    # handle flattened queries
    if query_nodes and query_nodes[-1] == "__flat__":
        return []

    stmt = sess.query(Node)

    if 'named_queries' in query_types and not query_nodes:
        # handled by incremental_query
        return []
    elif query_types[0] == 'named_queries':
        # handled by incremental_query
        return []

    num_params = expected_params(query_types)
    if not query_nodes or len(query_nodes) < num_params:
        # todo: query not complete: offer some virtual folders
        output = []
        return output

    parent_uri = '/'.join(query_nodes[num_params:])

    parent_path = uri_to_ltree(parent_uri)
    depth = uri_depth(parent_uri)

    stmt = sess.query(
        distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
    )

    stmt = stmt.filter(Node.path.op("<@")(parent_path))
    stmt = stmt.filter(func.nlevel(Node.path) > uri_depth(parent_uri)+1)

    if len(query_types) == 1 and query_types[0] == 'all':
        return [DummyNode(x[0].rsplit('.')[-1]) for x in stmt]

    # apply all filters in sequence
    for query_type in query_types:
        if query_type == 'date':
            stmt = dated(sess, stmt, parent_uri, query_nodes)

        if query_type == 'rating':
            stmt = rated(stmt, parent_uri, query_nodes)

        if query_type == 'major_mimetype':
            stmt = major_mimetype(stmt, parent_uri, query_nodes)

        if query_type == 'mimetype':
            stmt = mimetype(stmt, parent_uri, query_nodes)

        if query_type == 'aspect_range':
            stmt = aspect_range(stmt, parent_uri, query_nodes)

        if query_type == 'aspect':
            stmt = aspect(stmt, parent_uri, query_nodes)

        if query_type == 'md5':
            stmt = has_md5(stmt, parent_uri, query_nodes)

        if query_type == 'in_path':
            stmt = in_path(stmt, query_nodes)

        if query_type == 'tag':
            stmt = tagged(sess, stmt, parent_uri, query_nodes)

        if query_type == 'tag_group':
            stmt = in_tag_group(sess, stmt, parent_uri, query_nodes)

    return [DummyNode(x[0].rsplit('.', 1)[-1]) for x in stmt]


# --- Table definitions ------------------------------------------------------

class DummyNode(object):

    def __init__(self, label):
        self.label = label
        self.mimetype = 'other/directory'

    def __repr__(self):
        return "<DummyNode %s %r>" % (
            self.is_dir() and "d" or "f",
            self.label)

    def is_dir(self):
        return True

    @property
    def basename(self):
        return self.label

    @property
    def flatname(self):
        return self.label


class Node(Base, DummyNode):
    __tablename__ = 'node'
    uri = Column(Unicode, nullable=False, primary_key=True)
    path = Column(String, unique=True)
    md5 = Column(String(32))
    mimetype = Column(String(32))
    created = Column(DateTime)
    updated = Column(DateTime)
    to_purge = Column(Boolean, default=False)
    rating = Column(Integer, default=0)

    tags = relation(Tag, secondary=node_has_tag_table, backref='nodes')

    def __init__(self, uri):
        self.path = uri_to_ltree(uri)
        self.uri = uri

    def __repr__(self):
        return "<Node %s %r>" % (
            self.is_dir() and "d" or "f",
            self.uri)

    def is_dir(self):
        return self.mimetype == "other/directory"

    @property
    def basename(self):
        if self.uri == '/':
            return 'ROOT'
        return basename(self.uri)

    @property
    def md5name(self):
        from hashlib import md5
        if self.uri == '/':
            return 'ROOT'

        extension_parts = self.uri.rsplit('.', 1)
        if len(extension_parts) > 1:
            ext = extension_parts[-1]
        else:
            ext = ""

        out = "%s.%s" % (md5(self.uri).hexdigest(), ext)
        return out

    @property
    def flatname(self):
        parent_nodes = self.uri.split("/")
        if parent_nodes:
            parent_folder_hints = [x[0] for x in parent_nodes if x]
        else:
            parent_folder_hints = []
        return "_".join(parent_folder_hints) + "_" + basename(self.uri)

    @staticmethod
    def by_uri(session, uri):
        qry = session.query(Node)
        qry = qry.filter(Node.uri == uri)
        return qry.first()

    @staticmethod
    def by_path(session, path):
        qry = session.query(Node)
        qry = qry.filter(Node.path == path)
        return qry.first()

    def add_sparse_metadata(self):
        """
        Adds additional metadata into the HSTORE table
        """
        import Image
        if self.mimetype not in ('image/jpeg', ):
            return

        try:
            im = Image.open(self.uri)
        except IOError, exc:
            LOG.warning('Unable to add sparse metadata for %r (%s)' % (
                self, exc))
            return

        md5 = self.md5
        if not md5:
            md5 = file_md5(self.uri)
            upd = Node.__table__.update().where(
                Node.uri == self.uri).values(md5=md5)
        aspect_ratio = "%.3f" % (float(im.size[0]) / float(im.size[1]))
        values = dict(
            md5=md5,
            metadata=dict(
                dimensions="%s, %s" % im.size,
                aspect_ratio=aspect_ratio,
            ))
        try:
            ins = NodeMeta.__table__.insert().values(
                **values)
            ins.execute()
        except IntegrityError:
            upd = NodeMeta.__table__.update().where(
                NodeMeta.md5 == md5).values(**values)
            upd.execute()

    @staticmethod
    def update_one_node(sess, path, auto_tag_folder_tail=False,
                        auto_tag_words=None):
        from os.path import isfile, join
        import mimetypes
        auto_tag_words = auto_tag_words or []

        mimetypes.init()
        if not isfile(path):
            LOG.warning("Not a regular file: %r" % path)
            return

        if file == 'tag.hints':
            LOG.debug('Skipping tag.hints file')
            return

        mod_time = max(
            datetime.fromtimestamp(os.stat(path).st_mtime),
            datetime.fromtimestamp(os.stat(path).st_ctime)
        )
        create_time = datetime.fromtimestamp(os.stat(path).st_ctime)

        mimetype, _ = mimetypes.guess_type(path)

        auto_tags = set([])
        try:
            unipath = path.decode(getfilesystemencoding())
        except UnicodeEncodeError:
            LOG.error('Unable to encode %r using %s' % (
                path, getfilesystemencoding()))
            return
        if auto_tag_folder_tail:
            tailname = split(dirname(unipath))[-1]
            if tailname and len(tailname) > TAIL_DIR_THRESHOLD:
                auto_tags.add(tailname)
            else:
                LOG.warning("Not using %r as auto-tag-name. "
                            "Either it's empty or too short", tailname)

        if auto_tag_words:
            for word in auto_tag_words:
                if word.lower() in [x.lower()
                                    for x in splitpath(dirname(unipath))]:
                    auto_tags.add(word)

        db_node = sess.query(Node).filter_by(uri=unipath).first()
        if not db_node:
            db_node = Node(unipath)
            LOG.info("New node: %s" % (db_node, ))
        db_node.mimetype = mimetype
        Node.add_sparse_metadata(db_node)
        db_node.created = create_time
        db_node.updated = mod_time

        # process "tag.hints"
        #
        # the file contains a comma-separated list of tags applied to
        # all files in this folder
        #
        # If a line contains '::' the tags only apply to the filename
        # given before the '::' separator. Example:
        #
        # thefile.txt::documentation, project a, draft
        if not db_node.md5:
            LOG.info('Updating MD5')
            db_node.md5 = file_md5(unipath)
        unidir = dirname(unipath)
        hints_file = join(unidir, 'tag.hints')
        if exists(hints_file):
            for line in open(hints_file).readlines():
                if '::' not in line:
                    hint_tags = [_.strip() for _ in line.split(',')]
                    for tag in hint_tags:
                        auto_tags.add(tag)
                else:
                    filename, tags = line.split('::')
                    if file == filename.strip():
                        hint_tags = [_.strip() for _ in tags.split(',')]
                        for tag in hint_tags:
                            auto_tags.add(tag)

        if auto_tags:
            Node.set_tags(sess, db_node.md5, auto_tags, False)
            sess.add(db_node)
        LOG.info("Updated %s with tags %r" % (db_node, auto_tags))

    @staticmethod
    def update_from_query(sess, query, oldest_refresh=None,
                          auto_tag_folder_tail=False, auto_tag_words=None,
                          purge=False):

        auto_tag_words = auto_tag_words or []
        if not query.endswith('__flat__'):
            query += '/__flat__'

        result = Node.from_incremental_query(sess, query)
        for node in result:
            if not exists(node.uri) and purge:
                LOG.info("Purging %r" % node)
                sess.delete(node)
                continue
            elif not exists(node.uri):
                LOG.warning('Node %r is gone!' % node)
                continue
            Node.update_one_node(sess, node.uri, auto_tag_folder_tail,
                                 auto_tag_words)

    @staticmethod
    def update_nodes_from_path(sess, root, oldest_refresh=None,
                               auto_tag_folder_tail=False, auto_tag_words=None):

        auto_tag_words = auto_tag_words or []

        root_ltree = uri_to_ltree(root)
        if not oldest_refresh:
            oldest_refresh = select([func.max(Node.updated)])
            oldest_refresh = oldest_refresh.where(
                Node.path.op("<@")(root_ltree))
            oldest_refresh = oldest_refresh.execute().first()[0]

        LOG.info("Rescanning files that changed since %s" % oldest_refresh)

        for root, dirs, files in os.walk(root):

            if 'Thumbs.db' in files:
                files.remove('Thumbs.db')

            scanned_files = 0
            for file in files:
                path = abspath(join(root, file))
                Node.update_one_node(sess, path, auto_tag_folder_tail,
                                     auto_tag_words)
                scanned_files += 1

                mod_time = max(
                    datetime.fromtimestamp(os.stat(path).st_mtime),
                    datetime.fromtimestamp(os.stat(path).st_ctime)
                )

                # ignore files which have not been modified since last scan
                if oldest_refresh and mod_time < oldest_refresh:
                    continue

            if scanned_files > 0:
                LOG.info("commit")
                sess.commit()

            if 'CVS' in dirs:
                dirs.remove('CVS')  # don't visit CVS directories

            if '.git' in dirs:
                dirs.remove('.git')  # don't visit CVS directories

            if '.svn' in dirs:
                dirs.remove('.svn')  # don't visit CVS directories

        LOG.info("commit")
        sess.commit()

    @staticmethod
    def set_tags(sess, md5, new_tags, purge=True):
        query = node_has_tag_table.select()
        query = query.where(node_has_tag_table.c.md5 == md5)

        old_tags = []
        removals = []
        for row in sess.execute(query):
            old_tags.append(row.tag)

        if purge:
            for tag in old_tags:
                if tag not in new_tags:
                    removals.append(tag)

            for tag in removals:
                dquery = node_has_tag_table.delete()
                dquery = dquery.where(node_has_tag_table.c.name == tag)
                dquery = dquery.where(node_has_tag_table.c.md5 == md5)

        for tag_word in new_tags:
            tag = Tag.find(sess, tag_word)
            if not tag:
                tag = Tag(tag_word)
                if tag_word not in old_tags:
                    iquery = node_has_tag_table.insert()
                    iquery = iquery.values({
                        'md5': md5,
                        'tag': tag_word
                    })
                    sess.commit()
                    try:
                        sess.execute(iquery)
                        sess.commit()
                    except IntegrityError:
                        sess.rollback()

    @staticmethod
    def remove_empty_dirs(sess, root):
        root_ltree = uri_to_ltree(root)
        nodes = root_ltree.split('.')

        if not nodes:
            return

        qry = select([Node.path])
        qry = qry.where(Node.path.op("<@")('.'.join(nodes)))
        qry = qry.where(Node.mimetype == 'other/directory')
        child_nodes = [row[0] for row in qry.execute()]

        for node in child_nodes:
            qry = select([func.count(Node.uri)])
            qry = qry.where(Node.path.op("<@")(node))
            for row in qry.execute():
                if row[0] == 1:
                    LOG.debug('Removing empty dir: %r' % node)
                    Node.__table__.delete(Node.path == node).execute()

    @staticmethod
    def remove_orphans(sess, root):
        root_ltree = uri_to_ltree(root)
        qry = select([Node.uri, Node.mimetype])
        qry = qry.where(Node.path.op("<@")(root_ltree))
        for row in qry.execute():
            if not exists(row[0]):
                LOG.info('Removing orphan %r' % row[0])
                try:
                    Node.__table__.delete(Node.uri == row[0]).execute()
                    LOG.info("commit")
                    sess.commit()
                except:
                    sess.rollback()

        Node.remove_empty_dirs(sess, root)

    @staticmethod
    def calc_md5(sess, root, since=None):
        root_ltree = uri_to_ltree(root)
        qry = sess.query(Node)
        qry = qry.filter(Node.path.op("<@")(root_ltree))
        qry = qry.filter(Node.mimetype != 'other/directory')

        if since:
            qry = qry.filter(Node.updated >= since)

        count = 0
        for node in qry:
            if not exists(node.uri):
                continue
            node.md5 = file_md5(node.uri)
            LOG.info('Updated md5 of %s' % node)
            count += 1

            if count % 500 == 0:
                # commit from time to time
                LOG.info('commit')
                sess.commit()
        LOG.info('commit')
        sess.commit()

    @staticmethod
    def all(sess, nodes, flatten=False):

        parent_uri = '/'.join(nodes)

        parent_path = uri_to_ltree(parent_uri)
        depth = uri_depth(parent_uri)

        stmt = sess.query(
            distinct(func.subpath(Node.path, 0, depth + 1).label("subpath"))
        )

        stmt = stmt.filter(Node.path.op("<@")(parent_path))
        stmt = stmt.subquery()
        qry = sess.query(Node)
        qry = qry.filter(Node.path.in_(stmt))

        return qry

    @staticmethod
    def duplicates(sess):

        acks = select([AcknowledgedDuplicate.md5])

        qry = sess.query(Node.md5, func.count(Node.md5), func.max(Node.uri))
        qry = qry.filter(not_(Node.md5.in_(acks)))
        qry = qry.group_by(Node.md5)
        qry = qry.having(func.count(Node.md5) > 1)
        qry = qry.order_by(func.count(Node.md5).desc())
        return qry

    @staticmethod
    def set_rating(path, value):
        upd = Node.__table__.update()
        upd = upd.values(rating=value)
        upd = upd.where(Node.path == path)
        upd.execute()

    @staticmethod
    def one_image(sess, query, offset):
        stmt = Node.from_incremental_query(sess, query)
        stmt = stmt.filter(Node.mimetype != 'other/directory')
        stmt = stmt.limit(1).offset(offset)
        node = stmt.first()
        return node

    @staticmethod
    def from_incremental_query(sess, query):
        LOG.debug('parsing incremental query %r' % query)

        if not query or query == 'root' or query == '/':
            # list the available query schemes
            return [
                DummyNode('all'),
                DummyNode('date'),
                DummyNode('in_path'),
                DummyNode('md5'),
                DummyNode('named_queries'),
                DummyNode('rating'),
                DummyNode('tag'),
                DummyNode('tag_group'),
            ]
        else:
            if query.startswith('root'):
                query = query[5:]
            query_nodes = query.split('/')

        LOG.debug('Query nodes: %r' % query_nodes)

        # pop the query type off the beginning
        query_types = query_nodes.pop(0).lower()
        query_types = [x.strip() for x in query_types.split(',')]

        # handle flattened queries
        if query_nodes and query_nodes[-1] == "__flat__":
            query_nodes.pop()
            flatten = True
        else:
            flatten = False

        # Construct the different queries
        if len(query_types) == 1 and query_types[0] == 'all':
            return all(sess, query_nodes, flatten).order_by(Node.uri)

        if 'named_queries' in query_types and not query_nodes:
            nq_qry = sess.query(Query)
            nq_qry = nq_qry.filter(Query.label != None)
            nq_qry = nq_qry.order_by(Query.label)
            return [DummyNode(x.label) for x in nq_qry.all()]
        elif query_types[0] == 'named_queries':
            # fetch the saved query and replace the named query by that string
            query_name = query_nodes.pop(0)
            nq_qry = sess.query(Query)
            nq_qry = nq_qry.filter(Query.label == query_name).first()
            if not nq_qry:
                return []

            prepend_nodes = nq_qry.query.split('/')
            query_nodes = prepend_nodes + query_nodes

        num_params = expected_params(query_types)
        if not query_nodes or len(query_nodes) < num_params:
            # no all query parmeters known yet. Find appropriate queries
            output = []
            stmt = sess.query(Query.query)
            LOG.debug('Listing nodes starting with %r' % query)
            stmt = stmt.filter(Query.query.startswith(query))
            stmt = stmt.order_by(Query.query)
            for row in stmt:
                sub_nodes = row.query.split('/')
                # we're in the case where the initial nodes were empty. We only
                # return the next element
                output.append(DummyNode(sub_nodes[len(query_nodes)+1]))
            return output

        parent_uri = '/'.join(query_nodes[num_params:])

        parent_path = uri_to_ltree(parent_uri)
        depth = uri_depth(parent_uri)

        if flatten:
            stmt = sess.query(Node)
        else:
            stmt = sess.query(
                distinct(func.subpath(Node.path, 0, depth+1).label("subpath"))
            )

        stmt = stmt.filter(Node.path.op("<@")(parent_path))

        # apply all filters in sequence
        for query_type in query_types:
            if query_type == 'date':
                stmt = dated(sess, stmt, parent_uri, query_nodes)

            if query_type == 'major_mimetype':
                stmt = major_mimetype(stmt, parent_uri, query_nodes)

            if query_type == 'mimetype':
                stmt = mimetype(stmt, parent_uri, query_nodes)

            if query_type == 'rating':
                stmt = rated(stmt, parent_uri, query_nodes)

            if query_type == 'aspect':
                stmt = aspect(stmt, parent_uri, query_nodes)

            if query_type == 'aspect_range':
                stmt = aspect_range(stmt, parent_uri, query_nodes)

            if query_type == 'md5':
                stmt = has_md5(stmt, parent_uri, query_nodes)

            if query_type == 'in_path':
                stmt = in_path(stmt, query_nodes)

            if query_type == 'tag':
                stmt = tagged(sess, stmt, parent_uri, query_nodes)

            if query_type == 'tag_group':
                stmt = in_tag_group(sess, stmt, parent_uri, query_nodes)

        print stmt

        if not flatten:
            stmt = stmt.subquery()
            qry = sess.query(Node)
            qry = qry.filter(Node.path.in_(stmt))
            qry = qry.order_by(Node.uri)
            return qry

        return stmt.order_by(Node.uri)

    @staticmethod
    def delete_from_disk(sess, path):
        """
        Deletes an entry from disk and from the DB
        """
        from os import unlink
        node = sess.query(Node).filter(Node.path == path).first()
        if not node:
            return

        try:
            unlink(node.uri)
        except Exception, exc:
            LOG.exception(exc)

        sess.delete(node)
        LOG.info("commit")
        sess.commit()

    @staticmethod
    @memoized
    def map_to_fs(sess, query):
        """
        Remove any query specific elements, leaving only the fs-path
        """
        LOG.debug('Mapping to FS %r' % query)
        if query[0] == '/':
            query = query[1:]
        query_nodes = query.split("/")

        if not query_nodes:
            return None

        # pop the query type off the beginning
        query_types = query_nodes[0].lower()
        query_types = [x.strip() for x in query_types.split(',')]

        LOG.debug('Query types: %r' % query_types)
        chop_params = expected_params(query_types)
        LOG.debug('Expected number of params: %d' % chop_params)

        map_nodes = query_nodes[chop_params+1:]

        # Windows adds a wildcard. We'll remove it again...
        if map_nodes and map_nodes[-1] == '*':
            map_nodes.pop()

        if not map_nodes:
            return '/'

        if map_nodes[0] == 'ROOT' and '__flat__' not in map_nodes:
            LOG.debug('normal mapping of %r ' % map_nodes)
            map_nodes.pop(0)  # remove leading 'ROOT'

            LOG.info('remainder: %r' % map_nodes)
            out = '/' + '/'.join(map_nodes)
            return out

        elif map_nodes[-1] == '__flat__':
            return '/'

        elif map_nodes[-2] == '__flat__':

            mapping_base = query_nodes[0:-1]
            flatname = map_nodes[-1]

            LOG.debug('flattened mapping of %r ' % map_nodes)
            mapping_base = '/'.join(mapping_base)

            flatten_map = {}
            flatten_map[mapping_base] = {}

            stmt = Node.from_incremental_query(sess, mapping_base)
            for node in stmt:
                flatten_map[mapping_base][node.flatname] = node.uri
            return flatten_map[mapping_base].get(flatname, None)


class NodeMeta(Base):
    __tablename__ = 'node_meta'
    md5 = Column(String(32), primary_key=True)
    mdata = Column(HSTORE, name="metadata")


class AcknowledgedDuplicate(Base):
    __tablename__ = 'acknowledged_duplicates'
    md5 = Column(String, nullable=False, primary_key=True)

    def acknowledge_duplicate(sess, md5):
        AcknowledgedDuplicate.__table__.insert(values={'md5': md5}).execute()


# --- Filters -----------------------------------------------------------------

def expected_params(query_types):
    num = 0

    for type in query_types:

        if type == 'major_mimetype':
            num += 1

        if type == 'mimetype':
            num += 2

        if type == 'rating':
            num += 2

        if type == 'aspect':
            num += 2

        if type == 'aspect_range':
            num += 2

        if type == 'in_path':
            num += 1

        if type == 'md5':
            num += 1

        if type == 'date':
            num += 1

        if type == 'tag':
            num += 1

        if type == 'tag_group':
            num += 1

    return num


def rated(stmt, parent_uri, nodes):

    op = nodes.pop(0)
    value = int(nodes.pop(0))

    LOG.debug("Finding entries rated %s %2d in %s" % (op, value, parent_uri))

    if op == 'gt':
        stmt = stmt.filter(Node.rating > value)
    elif op == 'ge':
        stmt = stmt.filter(Node.rating >= value)
    elif op == 'lt':
        stmt = stmt.filter(Node.rating < value)
    elif op == 'le':
        stmt = stmt.filter(Node.rating <= value)
    elif op == 'eq':
        stmt = stmt.filter(Node.rating == value)
    elif op == 'ne':
        stmt = stmt.filter(Node.rating != value)

    return stmt


def mimetype(stmt, parent_uri, nodes):
    """
    Filter by mime type
    """

    mimetype_major = nodes.pop(0)
    mimetype_minor = nodes.pop(0)
    mimetype = '%s/%s' % (mimetype_major, mimetype_minor)

    stmt = stmt.filter(Node.mimetype == mimetype)

    return stmt


def major_mimetype(stmt, parent_uri, nodes):
    """
    Filter by major mime type (the part before the slash)
    """

    mimetype_major = nodes.pop(0)
    # TODO # SQL Injection possible right here!
    mimetype = '%s/%%' % (mimetype_major,)

    stmt = stmt.filter(Node.mimetype.like(mimetype))

    return stmt


def in_path(stmt, nodes):

    substring = nodes.pop(0)
    LOG.debug("Finding entries containing %s in path" % (substring))
    stmt = stmt.filter(Node.uri.ilike('%%%s%%' % substring))
    return stmt


def has_md5(stmt, parent_uri, nodes):

    md5 = nodes.pop(0)
    LOG.debug("Finding entries with md5 %s" % (md5))
    stmt = stmt.filter(Node.md5 == md5)
    return stmt


def dated(sess, stmt, parent_uri, nodes):

    date_string = nodes.pop(0)

    LOG.debug("Finding entries using date string %s in %r" % (
        date_string, parent_uri))

    match = TIME_PATTERN.match(date_string)
    if match and match.groups() != (None, None, None):
        groups = match.groups()
        if groups[0] and not groups[1] and not groups[2]:
            # matches 'yyyy-mm-dd'
            end_date = datetime.strptime(groups[0], "%Y-%m-%d")
            stmt = stmt.filter(Node.created < end_date)
        elif groups[0] and groups[1] == "t" and not groups[2]:
            # matches 'yyyy-mm-ddt'
            start_date = datetime.strptime(groups[0], "%Y-%m-%d")
            stmt = stmt.filter(Node.created > start_date)
        elif not groups[0] and groups[1] == "t" and groups[2]:
            # matches 'tyyyy-mm-dd'
            end_date = datetime.strptime(groups[2], "%Y-%m-%d")
            stmt = stmt.filter(Node.created < end_date)
        elif groups[0] and groups[1] == "t" and groups[2]:
            # matches 'yyyy-mm-ddtyyyy-mm-dd'
            start_date = datetime.strptime(groups[0], "%Y-%m-%d")
            end_date = datetime.strptime(groups[2], "%Y-%m-%d")
            stmt = stmt.filter(Node.created.between(start_date, end_date))
    else:
        timetuple = CALENDAR.parse(date_string)
        start_date = datetime(*timetuple[0][0:6])
        stmt = stmt.filter(Node.created > start_date)
    return stmt


def tagged(sess, stmt, parent_uri, nodes):
    """
    Find nodes with specific tags. Tags can be comma separated or
    plus-separated. Plus binds the tags in a conjunction, while commas use a
    disjunction. MRO: conjuction -> disjunction
    """

    tag_string = nodes.pop(0)

    LOG.debug("Finding entries using tag string %s in %r" % (
        tag_string, parent_uri))

    tagspec = [[x.strip() for x in _.strip().split('+')]
               for _ in tag_string.split(',')]
    LOG.debug("Parsed filters: %r" % tagspec)

    flat_tags = [item for sublist in tagspec for item in sublist]

    disjunctions = []
    tag_offset = 0
    for conjunction in tagspec:
        # complicated stuff to prevent SQL injections...
        placeholders = ', '.join([':tag_%d' % _
                                  for _ in range(tag_offset,
                                                 tag_offset + len(conjunction))
                                  ])
        sql = text('ARRAY[%s]' % placeholders, bindparams=[
            bindparam('tag_%d' % (tag_offset + pos), value)
            for pos, value in enumerate(conjunction)
        ])

        tmp = func.array_agg(node_has_tag_table.c.tag).op('@>')(sql)
        disjunctions.append(tmp)
        tag_offset += len(conjunction)

    subq = select([node_has_tag_table.c.md5])
    subq = subq.where(Tag.name.in_(flat_tags))
    subq = subq.group_by(node_has_tag_table.c.md5)
    subq = subq.having(or_(*disjunctions))

    stmt = stmt.filter(Node.md5.in_(subq))

    return stmt


def aspect(stmt, parent_uri, nodes):
    """
    Find all image nodes with the specified aspect ratio.

    Query parameters:

        op - Operator (string). One of:
            gt = Greater Than (>)
            lt = Less than (<)
            ge = greater than or equals (>=)
            le = less than or equals (<=)
            eq = equals (==)
            ne = not equals (!=)
        value - Aspect ratio (float)
    """

    op = nodes.pop(0)
    value = float(nodes.pop(0))

    subq = select([NodeMeta.md5])
    if op == 'gt':
        subq = subq.where(
            cast(NodeMeta.metadata.op('->')('aspect_ratio'),
                 Numeric(7, 3)) > value)
    elif op == 'ge':
        subq = subq.where(
            cast(NodeMeta.metadata.op('->')('aspect_ratio'),
                 Numeric(7, 3)) >= value)
    elif op == 'lt':
        subq = subq.where(
            cast(NodeMeta.metadata.op('->')('aspect_ratio'),
                 Numeric(7, 3)) < value)
    elif op == 'le':
        subq = subq.where(
            cast(NodeMeta.metadata.op('->')('aspect_ratio'),
                 Numeric(7, 3)) <= value)
    elif op == 'eq':
        subq = subq.where(
            cast(NodeMeta.metadata.op('->')('aspect_ratio'),
                 Numeric(7, 3)) == value)
    elif op == 'ne':
        subq = subq.where(
            cast(NodeMeta.metadata.op('->')('aspect_ratio'),
                 Numeric(7, 3)) != value)

    stmt = stmt.filter(Node.md5.in_(subq))

    return stmt


def aspect_range(stmt, parent_uri, nodes):
    """
    Find all image nodes having an aspect ratio between two values

    Query parameters:

        value_min - Aspect ratio (float)
        value_max - Aspect ratio (float)
    """

    value_min = float(nodes.pop(0))
    value_max = float(nodes.pop(0))

    subq = select([NodeMeta.md5])
    subq = subq.where(
        cast(NodeMeta.metadata.op('->')('aspect_ratio'),
             Numeric(7, 3)) >= value_min)
    subq = subq.where(
        cast(NodeMeta.metadata.op('->')('aspect_ratio'),
             Numeric(7, 3)) <= value_max)

    stmt = stmt.filter(Node.md5.in_(subq))

    return stmt


def in_tag_group(sess, stmt, parent_uri, nodes):

    group_string = nodes.pop(0)

    LOG.debug("Finding entries using tag group string %s in %r" % (
        group_string, parent_uri))

    groups = group_string.split(',')

    # select tag names
    tags = select([tag_in_tag_group_table.c.tagname])
    tags = tags.where(tag_in_tag_group_table.c.groupname.in_(groups))

    # pick out md5sums which are tagged with those tags
    md5sums = select([node_has_tag_table.c.md5])
    md5sums = md5sums.where(node_has_tag_table.c.tag.in_(tags))

    # filter the current query given these tags
    stmt = stmt.filter(Node.md5.in_(md5sums))

    return stmt
