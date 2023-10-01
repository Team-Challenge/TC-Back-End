"""Add phone_number column to User

Revision ID: 160781c47b29
Revises: c4e1a82b4b60
Create Date: 2023-09-30 14:43:26.863724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '160781c47b29'
down_revision = 'c4e1a82b4b60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone_number', sa.String(length=15), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('phone_number')

    # ### end Alembic commands ###
