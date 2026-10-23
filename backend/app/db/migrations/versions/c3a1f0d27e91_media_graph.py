"""media graph

Revision ID: c3a1f0d27e91
Revises: bac86c178da8
Create Date: 2026-10-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a1f0d27e91'
down_revision: Union[str, Sequence[str], None] = 'bac86c178da8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MEDIA_TYPES = ('book', 'tv_show', 'film', 'game', 'podcast', 'other')


def upgrade() -> None:
    """Upgrade schema."""
    media_type = sa.Enum(*MEDIA_TYPES, name='media_type')

    op.create_table('media',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('creator', sa.Text(), nullable=False),
    sa.Column('media_type', media_type, nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_media'))
    )
    op.create_index(op.f('ix_media_created_at'), 'media', ['created_at'], unique=False)
    op.create_index(op.f('ix_media_media_type'), 'media', ['media_type'], unique=False)
    op.create_index(op.f('ix_media_updated_at'), 'media', ['updated_at'], unique=False)

    op.create_table('theme',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_theme')),
    sa.UniqueConstraint('name', name=op.f('uq_theme_name'))
    )
    op.create_index(op.f('ix_theme_created_at'), 'theme', ['created_at'], unique=False)
    op.create_index(op.f('ix_theme_updated_at'), 'theme', ['updated_at'], unique=False)

    op.create_table('media_theme',
    sa.Column('media_id', sa.Integer(), nullable=False),
    sa.Column('theme_id', sa.Integer(), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['media_id'], ['media.id'], name=op.f('fk_media_theme_media_id_media'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['theme_id'], ['theme.id'], name=op.f('fk_media_theme_theme_id_theme'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('media_id', 'theme_id', name=op.f('pk_media_theme'))
    )
    op.create_index(op.f('ix_media_theme_theme_id'), 'media_theme', ['theme_id'], unique=False)

    op.create_table('media_link',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=False),
    sa.Column('target_id', sa.Integer(), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.CheckConstraint('source_id < target_id', name=op.f('ck_media_link_ordered_pair')),
    sa.ForeignKeyConstraint(['source_id'], ['media.id'], name=op.f('fk_media_link_source_id_media'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['target_id'], ['media.id'], name=op.f('fk_media_link_target_id_media'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_media_link')),
    sa.UniqueConstraint('source_id', 'target_id', name='uq_media_link_pair')
    )
    op.create_index(op.f('ix_media_link_created_at'), 'media_link', ['created_at'], unique=False)
    op.create_index(op.f('ix_media_link_target_id'), 'media_link', ['target_id'], unique=False)
    op.create_index(op.f('ix_media_link_updated_at'), 'media_link', ['updated_at'], unique=False)

    op.create_table('media_link_theme',
    sa.Column('link_id', sa.Integer(), nullable=False),
    sa.Column('theme_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['link_id'], ['media_link.id'], name=op.f('fk_media_link_theme_link_id_media_link'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['theme_id'], ['theme.id'], name=op.f('fk_media_link_theme_theme_id_theme'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('link_id', 'theme_id', name=op.f('pk_media_link_theme'))
    )
    op.create_index(op.f('ix_media_link_theme_theme_id'), 'media_link_theme', ['theme_id'], unique=False)

    # Reshape review: each existing review becomes a media row (type 'book') plus a review on it.
    op.add_column('review', sa.Column('media_id', sa.Integer(), nullable=True))
    op.add_column('review', sa.Column('body', sa.Text(), nullable=True))
    # Reuse each review's id as its media id, so no row matching is needed.
    op.execute(
        """
        INSERT INTO media (id, title, creator, media_type, created_at, updated_at)
        SELECT id, name, author, 'book', created_at, updated_at FROM review
        """
    )
    op.execute("UPDATE review SET media_id = id")
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('media', 'id'),
            COALESCE(MAX(id), 1),
            MAX(id) IS NOT NULL
        ) FROM media
        """
    )
    op.alter_column('review', 'media_id', nullable=False)
    op.create_unique_constraint(op.f('uq_review_media_id'), 'review', ['media_id'])
    op.create_foreign_key(op.f('fk_review_media_id_media'), 'review', 'media', ['media_id'], ['id'], ondelete='CASCADE')
    op.drop_column('review', 'name')
    op.drop_column('review', 'author')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('review', sa.Column('name', sa.Text(), nullable=True))
    op.add_column('review', sa.Column('author', sa.Text(), nullable=True))
    op.execute(
        """
        UPDATE review r SET name = m.title, author = m.creator
        FROM media m WHERE m.id = r.media_id
        """
    )
    op.alter_column('review', 'name', nullable=False)
    op.alter_column('review', 'author', nullable=False)
    op.drop_constraint(op.f('fk_review_media_id_media'), 'review', type_='foreignkey')
    op.drop_constraint(op.f('uq_review_media_id'), 'review', type_='unique')
    op.drop_column('review', 'body')
    op.drop_column('review', 'media_id')

    op.drop_index(op.f('ix_media_link_theme_theme_id'), table_name='media_link_theme')
    op.drop_table('media_link_theme')
    op.drop_index(op.f('ix_media_link_updated_at'), table_name='media_link')
    op.drop_index(op.f('ix_media_link_target_id'), table_name='media_link')
    op.drop_index(op.f('ix_media_link_created_at'), table_name='media_link')
    op.drop_table('media_link')
    op.drop_index(op.f('ix_media_theme_theme_id'), table_name='media_theme')
    op.drop_table('media_theme')
    op.drop_index(op.f('ix_theme_updated_at'), table_name='theme')
    op.drop_index(op.f('ix_theme_created_at'), table_name='theme')
    op.drop_table('theme')
    op.drop_index(op.f('ix_media_updated_at'), table_name='media')
    op.drop_index(op.f('ix_media_media_type'), table_name='media')
    op.drop_index(op.f('ix_media_created_at'), table_name='media')
    op.drop_table('media')
    sa.Enum(name='media_type').drop(op.get_bind(), checkfirst=True)
