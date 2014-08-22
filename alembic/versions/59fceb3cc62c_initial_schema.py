"""initial_schema

Revision ID: 59fceb3cc62c
Revises: None
Create Date: 2014-08-21 18:45:14.111363

"""

# revision identifiers, used by Alembic.
revision = '59fceb3cc62c'
down_revision = None

from alembic import op
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Unicode,
)
from sqlalchemy.dialects.postgresql import HSTORE


def upgrade():

    op.create_table(
        'node',
        Column('uri', Unicode, nullable=False, primary_key=True),
        Column('path', String, unique=True),
        Column('md5', String(32)),
        Column('mimetype', String(32)),
        Column('created', DateTime),
        Column('updated', DateTime),
        Column('to_purge', Boolean, default=False),
        Column('rating', Integer, default=0),
    )

    op.create_table(
        'node_meta',
        Column('md5', String(32), primary_key=True),
        Column('metadata', HSTORE)
    )

    op.create_table(
        'acknowledged_duplicates',
        Column('md5', String, nullable=False, primary_key=True)
    )

    op.create_table(
        'query',
        Column('query', String, nullable=False, primary_key=True),
        Column('label', String, nullable=True, default=None)
    )

    op.create_table(
        'tag_group',
        Column('name', Unicode, nullable=False, primary_key=True)
    )

    op.create_table(
        'tag',
        Column('name', Unicode, nullable=False, primary_key=True)
    )

    op.create_table(
        'tag_in_tag_group',
        Column('tagname', Unicode,
               ForeignKey('tag.name', onupdate="CASCADE", ondelete='CASCADE'),
               nullable=False, primary_key=True),
        Column('groupname', Unicode,
               ForeignKey('tag_group.name', onupdate="CASCADE",
                          ondelete='CASCADE'),
               nullable=False, primary_key=True),
    )

    op.create_table(
        'node_has_tag',
        Column('md5', String(32), nullable=False, primary_key=True),
        Column('tag', Unicode,
               ForeignKey('tag.name'), nullable=False, primary_key=True),
    )


def downgrade():
    op.drop_table('node_has_tag')
    op.drop_table('tag_in_tag_group')
    op.drop_table('tag')
    op.drop_table('tag_group')
    op.drop_table('query')
    op.drop_table('acknowledged_duplicates')
    op.drop_table('node_meta')
    op.drop_table('node')
