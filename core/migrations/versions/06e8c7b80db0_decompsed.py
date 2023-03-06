"""decompsed

Revision ID: 06e8c7b80db0
Revises: fcb5b57a1a68
Create Date: 2023-03-06 18:44:14.599485

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '06e8c7b80db0'
down_revision = 'fcb5b57a1a68'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('child_matched_products',
    sa.Column('nm_id', sa.Integer(), nullable=False),
    sa.Column('product', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('parent_nm_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_nm_id'], ['matched_products.nm_id'], ),
    sa.PrimaryKeyConstraint('nm_id')
    )
    op.drop_column('matched_products', 'matched_products')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('matched_products', sa.Column('matched_products', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_table('child_matched_products')
    # ### end Alembic commands ###
