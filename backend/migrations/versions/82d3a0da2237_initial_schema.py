"""initial_schema

Revision ID: 82d3a0da2237
Revises:
Create Date: 2026-08-15T05:18:56.567681+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82d3a0da2237'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### DomKG initial schema (from SQLAlchemy metadata) ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=True)

    op.create_table('cities',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.UniqueConstraint('name'),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_cities_slug', 'cities', ['slug'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_phone', 'users', ['phone'], unique=True)

    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=30), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_admins_user_id', 'admins', ['user_id'], unique=True)

    op.create_table('districts',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('city_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE')
    )

    op.create_index('ix_districts_city_id', 'districts', ['city_id'])
    op.create_index('ix_districts_slug', 'districts', ['slug'], unique=True)

    op.create_table('properties',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('city_id', sa.Integer(), nullable=False),
    sa.Column('district_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('deal_type', sa.String(length=10), nullable=False),
    sa.Column('property_type', sa.String(length=20), nullable=False),
    sa.Column('price', sa.Numeric(14, 2), nullable=False),
    sa.Column('price_per_m2', sa.Numeric(14, 2), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('area_total', sa.Numeric(10, 2), nullable=True),
    sa.Column('area_living', sa.Numeric(10, 2), nullable=True),
    sa.Column('area_kitchen', sa.Numeric(10, 2), nullable=True),
    sa.Column('rooms', sa.Integer(), nullable=True),
    sa.Column('floor', sa.Integer(), nullable=True),
    sa.Column('floor_total', sa.Integer(), nullable=True),
    sa.Column('bathrooms', sa.Integer(), nullable=True),
    sa.Column('year_built', sa.Integer(), nullable=True),
    sa.Column('has_parking', sa.Boolean(), nullable=False),
    sa.Column('has_balcony', sa.Boolean(), nullable=False),
    sa.Column('has_furniture', sa.Boolean(), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('latitude', sa.Numeric(9, 6), nullable=True),
    sa.Column('longitude', sa.Numeric(9, 6), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('is_featured', sa.Boolean(), nullable=False),
    sa.Column('view_count', sa.Integer(), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE')
    )

    op.create_index('ix_properties_category_id', 'properties', ['category_id'])
    op.create_index('ix_properties_city_id', 'properties', ['city_id'])
    op.create_index('ix_properties_district_id', 'properties', ['district_id'])
    op.create_index('ix_properties_owner_id', 'properties', ['owner_id'])
    op.create_index('ix_properties_status', 'properties', ['status'])
    op.create_index('ix_properties_status_deal', 'properties', ['status', 'deal_type'])

    op.create_table('favorites',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.UniqueConstraint('user_id', 'property_id', name='uq_favorites_user_property'),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_favorites_property_id', 'favorites', ['property_id'])
    op.create_index('ix_favorites_user_id', 'favorites', ['user_id'])

    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('receiver_id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=True),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE')
    )

    op.create_index('ix_messages_property_id', 'messages', ['property_id'])
    op.create_index('ix_messages_receiver_id', 'messages', ['receiver_id'])
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'])

    op.create_table('property_images',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=500), nullable=False),
    sa.Column('alt_text', sa.String(length=200), nullable=True),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_property_images_property_id', 'property_images', ['property_id'])

    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('reporter_id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('resolved_by', sa.Integer(), nullable=True),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('resolution_note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['resolved_by'], ['admins.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_reports_property_id', 'reports', ['property_id'])
    op.create_index('ix_reports_reporter_id', 'reports', ['reporter_id'])
    op.create_index('ix_reports_status', 'reports', ['status'])

    op.create_table('views',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('user_agent', sa.String(length=255), nullable=True),
    sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )

    op.create_index('ix_views_property_id', 'views', ['property_id'])
    op.create_index('ix_views_user_id', 'views', ['user_id'])

    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=30), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('property_id', sa.Integer(), nullable=True),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='SET NULL')
    )

    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])



def downgrade():
    # ### drop tables in reverse dependency order ###
    op.drop_table('notifications')
    op.drop_table('views')
    op.drop_table('reports')
    op.drop_table('property_images')
    op.drop_table('messages')
    op.drop_table('favorites')
    op.drop_table('properties')
    op.drop_table('districts')
    op.drop_table('admins')
    op.drop_table('users')
    op.drop_table('cities')
    op.drop_table('categories')
