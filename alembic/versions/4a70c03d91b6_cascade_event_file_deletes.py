"""cascade_event_file_deletes

Revision ID: 4a70c03d91b6
Revises: e88bc62b6e4
Create Date: 2015-03-17 15:43:41.023763

"""

# revision identifiers, used by Alembic.
revision = '4a70c03d91b6'
down_revision = 'e88bc62b6e4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("event_files_event_id_fkey", 'event_files')
    op.create_foreign_key('event_files_event_id_fkey', 'event_files', 'event', ['event_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint("event_files_file_id_fkey", 'event_files')
    op.create_foreign_key('event_files_file_id_fkey', 'event_files', 'file', ['file_id'], ['id'], ondelete='CASCADE')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###
