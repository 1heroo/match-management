"""added new column in child model

Revision ID: f72a38c6498c
Revises: 2657f08ea471
Create Date: 2023-03-08 00:08:49.771909

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f72a38c6498c'
down_revision = '2657f08ea471'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('child_matched_products', sa.Column('price', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('child_matched_products', 'price')
    # ### end Alembic commands ###
