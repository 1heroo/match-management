"""added new column in child model

Revision ID: 515d0cc57c40
Revises: f72a38c6498c
Create Date: 2023-03-08 00:12:18.529409

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '515d0cc57c40'
down_revision = 'f72a38c6498c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('child_matched_products', sa.Column('parent_nm_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('child_matched_products', 'parent_nm_id')
    # ### end Alembic commands ###
