from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
    Unicode,
    desc,
    func,
    select,
)

from metafilter.model import Base


# --- Table definitions ------------------------------------------------------

tag_in_tag_group_table = Table(
    'tag_in_tag_group', Base.metadata,
    Column('tagname', Unicode,
           ForeignKey('tag.name', onupdate="CASCADE", ondelete='CASCADE'),
           nullable=False, primary_key=True),
    Column('groupname', Unicode,
           ForeignKey('tag_group.name', onupdate="CASCADE", ondelete='CASCADE'),
           nullable=False, primary_key=True),
)

node_has_tag_table = Table(
    'node_has_tag', Base.metadata,
    Column('md5', String(32),
           ForeignKey('node.md5'), nullable=False, primary_key=True),
    Column('tag', Unicode,
           ForeignKey('tag.name'), nullable=False, primary_key=True),
)


class Tag(Base):

    __tablename__ = 'tag'

    name = Column(Unicode, nullable=False, primary_key=True)

    @staticmethod
    def counts(sess):
        tags = select([node_has_tag_table.c.tag, func.count().label('count')])
        tags = tags.order_by(desc('count'))
        tags = tags.group_by(node_has_tag_table.c.tag)
        return tags

    @classmethod
    def find(self, sess, name):
        qry = sess.query(Tag)
        qry = qry.filter(Tag.name == name)
        return qry.first()

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Tag %r>' % self.name

    def __str__(self):
        return self.name
