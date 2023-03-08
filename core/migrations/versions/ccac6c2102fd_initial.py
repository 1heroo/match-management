"""initial

Revision ID: ccac6c2102fd
Revises: 
Create Date: 2023-03-09 00:54:50.859429

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ccac6c2102fd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('brands',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('percentage', sa.Integer(), nullable=True),
    sa.Column('brand_id', sa.Integer(), nullable=True),
    sa.Column('min_step', sa.Integer(), nullable=True),
    sa.Column('is_included_to_pm', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('matched_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nm_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('subj_name', sa.String(), nullable=True),
    sa.Column('brand', sa.String(), nullable=True),
    sa.Column('brand_id', sa.Integer(), nullable=True),
    sa.Column('subj_root_name', sa.String(), nullable=True),
    sa.Column('vendor_code', sa.String(), nullable=True),
    sa.Column('min_price', sa.Integer(), nullable=True),
    sa.Column('the_product', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('checked_nms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nm_id', sa.Integer(), nullable=True),
    sa.Column('product', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('child_matched_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nm_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('vendor_name', sa.String(), nullable=True),
    sa.Column('vendor_code', sa.String(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('parent_nm_id', sa.Integer(), nullable=True),
    sa.Column('brand', sa.String(), nullable=True),
    sa.Column('brand_id', sa.Integer(), nullable=True),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('product', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['matched_products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('child_matched_products')
    op.drop_table('products')
    op.drop_table('matched_products')
    op.drop_table('brands')
    # ### end Alembic commands ###
