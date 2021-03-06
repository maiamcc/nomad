"""add uuid for visible keys

Revision ID: bb34f3d9a8f4
Revises: e356e6efd25d
Create Date: 2017-09-30 11:37:24.898992

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bb34f3d9a8f4'
down_revision = 'e356e6efd25d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('carpools', sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_carpools_uuid'), 'carpools', ['uuid'], unique=False)
    op.add_column('destinations', sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_destinations_uuid'), 'destinations', ['uuid'], unique=False)
    op.add_column('people', sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_people_uuid'), 'people', ['uuid'], unique=False)
    op.add_column('riders', sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_riders_uuid'), 'riders', ['uuid'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_riders_uuid'), table_name='riders')
    op.drop_column('riders', 'uuid')
    op.drop_index(op.f('ix_people_uuid'), table_name='people')
    op.drop_column('people', 'uuid')
    op.drop_index(op.f('ix_destinations_uuid'), table_name='destinations')
    op.drop_column('destinations', 'uuid')
    op.drop_index(op.f('ix_carpools_uuid'), table_name='carpools')
    op.drop_column('carpools', 'uuid')
    # ### end Alembic commands ###
