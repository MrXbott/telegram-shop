"""add image_id field for product

Revision ID: 9b969e69ac6d
Revises: 3c5dd3c4dc8e
Create Date: 2025-05-08 12:37:18.131038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b969e69ac6d'
down_revision: Union[str, None] = '3c5dd3c4dc8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('image_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'image_id')
    # ### end Alembic commands ###
