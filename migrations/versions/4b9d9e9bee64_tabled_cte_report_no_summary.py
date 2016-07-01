"""tabled-cte-report-no-summary

Revision ID: 4b9d9e9bee64
Revises: 48b2bb4f986a
Create Date: 2016-06-30 12:23:41.997905

"""

# revision identifiers, used by Alembic.
revision = '4b9d9e9bee64'
down_revision = '48b2bb4f986a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tabled_committee_report', 'summary')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tabled_committee_report', sa.Column('summary', sa.TEXT(), autoincrement=False, nullable=True))
    ### end Alembic commands ###