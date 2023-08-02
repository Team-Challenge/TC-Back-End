"""update users2

Revision ID: 264d781c3414
Revises: 90cccca9d593
Create Date: 2023-08-02 09:18:11.696795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '264d781c3414'
down_revision = '90cccca9d593'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('joined_at', sa.DateTime(), nullable=True))
    op.drop_column('users', 'admin')
    op.drop_column('users', 'password')
    op.drop_column('users', 'date_registered')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('date_registered', sa.DATETIME(), nullable=True))
    op.add_column('users', sa.Column('password', sa.VARCHAR(length=50), nullable=True))
    op.add_column('users', sa.Column('admin', sa.BOOLEAN(), nullable=True))
    op.drop_column('users', 'joined_at')
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###
