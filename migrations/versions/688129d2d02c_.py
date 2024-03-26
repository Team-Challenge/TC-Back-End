"""empty message

Revision ID: 688129d2d02c
Revises: 07599ad332f5
Create Date: 2024-03-10 15:37:37.363143

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '688129d2d02c'
down_revision = '07599ad332f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_details', schema=None) as batch_op:
        batch_op.alter_column('delivery_post',
               existing_type=sa.VARCHAR(length=9),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.alter_column('method_of_payment',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_details', schema=None) as batch_op:
        batch_op.alter_column('method_of_payment',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('delivery_post',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=9),
               existing_nullable=True)

    # ### end Alembic commands ###
