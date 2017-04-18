"""add preferred contact

Revision ID: c67cdff93954
Revises: f70474acd7db
Create Date: 2017-04-17 20:48:14.186398

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = 'c67cdff93954'
down_revision = 'f70474acd7db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('people', sa.Column('preferred_contact_method', sa.String(length=80), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('people', 'preferred_contact_method')
    # ### end Alembic commands ###