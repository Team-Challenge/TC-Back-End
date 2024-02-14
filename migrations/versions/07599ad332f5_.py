"""empty message

Revision ID: 07599ad332f5
Revises: 980a7079cd93
Create Date: 2024-02-13 21:36:43.790727

"""
from alembic import op
import sqlalchemy as sa



revision = '07599ad332f5'
down_revision = '980a7079cd93'
branch_labels = None
depends_on = None


def upgrade():

    op.drop_table('product_raitings')
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.create_unique_constraint("unique_category_name", ['category_name'])

    with op.batch_alter_table('product_comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('raiting', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('time_added', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('is_confirmed_purchase', sa.Boolean(), nullable=True))



def downgrade():

    with op.batch_alter_table('product_comment', schema=None) as batch_op:
        batch_op.drop_column('is_confirmed_purchase')
        batch_op.drop_column('time_added')
        batch_op.drop_column('raiting')

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_constraint("unique_category_name", type_='unique')

    op.create_table('product_raitings',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('product_id', sa.INTEGER(), nullable=True),
    sa.Column('product_rating', sa.FLOAT(), nullable=True),
    sa.Column('votes', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

