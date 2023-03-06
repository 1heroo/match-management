"""added new model, changed columns

Revision ID: fcb5b57a1a68
Revises: 80a0e470ca62
Create Date: 2023-03-03 12:19:36.913180

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fcb5b57a1a68'
down_revision = '80a0e470ca62'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('matched_products',
    sa.Column('nm_id', sa.Integer(), nullable=False),
    sa.Column('the_product', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('matched_products', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('nm_id')
    )
    op.add_column('products', sa.Column('product', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.drop_column('products', 'detail')
    op.drop_column('products', 'seller_data')
    op.drop_column('products', 'card')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('card', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('products', sa.Column('seller_data', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('products', sa.Column('detail', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_column('products', 'product')
    op.drop_table('matched_products')
    # ### end Alembic commands ###
