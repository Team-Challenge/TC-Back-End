"""Rename old tables, create new tables, drop old tables

Revision ID: a045f13dc2de
Revises: 305158487226
Create Date: 2024-01-12 11:36:27.478276

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a045f13dc2de'
down_revision = '305158487226'
branch_labels = None
depends_on = None


def upgrade():
    # Rename old tables
    op.rename_table('products', 'old_products')
    op.rename_table('order_status', 'old_order_status')
    op.rename_table('orders', 'old_orders')
    op.rename_table('product_category', 'old_product_category')
    op.rename_table('product_order', 'old_product_order')
    op.rename_table('products_photos', 'old_products_photos')

    # Create new tables
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('sub_category_name', sa.Enum('заколки', 'обручі', 'резинки', 'хустинки', 'сережки', 'моносережки', 'згарди', 'шелести', 'гердани', 'силянки', 'кризи', 'чокери', 'намиста', 'дукачі', 'кулони та підвіски', 'браслети', 'каблучки', 'котильйони', 'брошки', 'сумки', name='sub_category_enum'), nullable=True),
        sa.Column('shop_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=100), nullable=False),
        sa.Column('product_description', sa.String(length=1000), nullable=True),
        sa.Column('time_added', sa.DateTime(), nullable=True),
        sa.Column('time_modifeid', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
        sa.PrimaryKeyConstraint('id'))

    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('product_status', sa.Enum('В наявності', 'Під замовлення', 'В єдиному екземплярі', 'Немає в наявності', name='product_status'), nullable=True),
        sa.Column('product_characteristic', sa.Text(), nullable=True),
        sa.Column('is_return', sa.Boolean(), nullable=False),
        sa.Column('delivery_post', sa.Enum('nova_post', 'ukr_post', name='delivery_post'), nullable=True),
        sa.Column('method_of_payment', sa.String(), nullable=True),
        sa.Column('is_unique', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_rating', sa.Float(), nullable=False),
        sa.Column('votes', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_detail_id', sa.Integer(), nullable=True),
        sa.Column('product_photo', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('main', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['product_detail_id'], ['product_details.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Drop old tables
    op.drop_table('old_products')
    op.drop_table('old_order_status')
    op.drop_table('old_orders')
    op.drop_table('old_product_category')
    op.drop_table('old_product_order')
    op.drop_table('old_products_photos')


def downgrade():
    # Drop the new tables
    op.drop_table('product_photos')
    op.drop_table('product_ratings')
    op.drop_table('product_details')
    op.drop_table('product_comment')
    op.drop_table('categories')
    op.drop_table('products')


