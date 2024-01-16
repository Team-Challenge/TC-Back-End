"""empty message

Revision ID: 980a7079cd93
Revises: 
Create Date: 2024-01-15 20:32:29.433007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '980a7079cd93'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('joined_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('profile_picture', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('delivery_user_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('post', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('branch_name', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('security',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('password_hash', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('shops',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('photo_shop', sa.String(), nullable=True),
    sa.Column('banner_shop', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('link', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('sub_category_name', sa.Enum('заколки', 'обручі', 'резинки', 'хустинки', 'сережки', 'моносережки', 'згарди', 'шелести', 'гердани', 'силянки', 'кризи', 'чокери', 'намиста', 'дукачі', 'кулони та підвіски', 'браслети', 'каблучки', 'котильйони', 'брошки', 'сумки', name='sub_category_enum'), nullable=True),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.Column('product_name', sa.String(length=100), nullable=True),
    sa.Column('product_description', sa.String(length=1000), nullable=True),
    sa.Column('time_added', sa.DateTime(), nullable=True),
    sa.Column('time_modifeid', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('comment', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('product_status', sa.Enum('В наявності', 'Під замовлення', 'В єдиному екземплярі', 'Немає в наявності', name='product_status'), nullable=True),
    sa.Column('product_characteristic', sa.Text(), nullable=True),
    sa.Column('is_return', sa.Boolean(), nullable=True),
    sa.Column('delivery_post', sa.Enum('nova_post', 'ukr_post', name='delivery_post'), nullable=True),
    sa.Column('method_of_payment', sa.String(), nullable=True),
    sa.Column('is_unique', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_raitings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('product_rating', sa.Float(), nullable=True),
    sa.Column('votes', sa.Integer(), nullable=True),
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


def downgrade():
    op.drop_table('product_photos')
    op.drop_table('product_raitings')
    op.drop_table('product_details')
    op.drop_table('product_comment')
    op.drop_table('products')
    op.drop_table('shops')
    op.drop_table('security')
    op.drop_table('delivery_user_info')
    op.drop_table('users')
    op.drop_table('categories')
