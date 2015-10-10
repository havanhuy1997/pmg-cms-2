"""rename-saved-search-table

Revision ID: 625399a9e26
Revises: 3bf259540e8b
Create Date: 2015-10-10 08:24:33.215772

"""

# revision identifiers, used by Alembic.
revision = '625399a9e26'
down_revision = '3bf259540e8b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('saved_search',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('search', sa.String(length=255), nullable=False),
    sa.Column('content_type', sa.String(length=255), nullable=True),
    sa.Column('committee_id', sa.Integer(), nullable=True),
    sa.Column('last_alerted_at', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True),
    sa.ForeignKeyConstraint(['committee_id'], ['committee.id'], name=op.f('fk_saved_search_committee_id_committee'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_saved_search_user_id_user'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_saved_search'))
    )
    op.create_index(op.f('ix_saved_search_created_at'), 'saved_search', ['created_at'], unique=False)
    op.drop_table('search_alert')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('search_alert',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('search', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('content_type', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('committee_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('last_alerted_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text(u'now()'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text(u'now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['committee_id'], [u'committee.id'], name=u'search_alert_committee_id_fkey', ondelete=u'CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], [u'user.id'], name=u'search_alert_user_id_fkey', ondelete=u'CASCADE'),
    sa.PrimaryKeyConstraint('id', name=u'search_alert_pkey')
    )
    op.drop_index(op.f('ix_saved_search_created_at'), table_name='saved_search')
    op.drop_table('saved_search')
    ### end Alembic commands ###