"""add date to static pages

Revision ID: 83d52ae7dd2
Revises: 39f25296cd6
Create Date: 2017-06-29 16:50:36.320289

"""

# revision identifiers, used by Alembic.
revision = '83d52ae7dd2'
down_revision = '39f25296cd6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('page', sa.Column('date', sa.Date(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('page', 'date')
    ### end Alembic commands ###
