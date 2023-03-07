"""renamed field in child model 

Revision ID: 4f50b9829cc1
Revises: 6af0aab5f24c
Create Date: 2023-03-07 19:55:37.520178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f50b9829cc1'
down_revision = '6af0aab5f24c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('child_matched_products', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.drop_constraint('child_matched_products_parent_nm_id_fkey', 'child_matched_products', type_='foreignkey')
    op.create_foreign_key(None, 'child_matched_products', 'matched_products', ['parent_id'], ['id'])
    op.drop_column('child_matched_products', 'parent_nm_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('child_matched_products', sa.Column('parent_nm_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'child_matched_products', type_='foreignkey')
    op.create_foreign_key('child_matched_products_parent_nm_id_fkey', 'child_matched_products', 'matched_products', ['parent_nm_id'], ['id'])
    op.drop_column('child_matched_products', 'parent_id')
    # ### end Alembic commands ###
