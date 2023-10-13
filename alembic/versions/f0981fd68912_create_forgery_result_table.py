"""create_forgery_result_table

Revision ID: f0981fd68912
Revises: 
Create Date: 2023-10-12 22:02:35.172692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0981fd68912'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'forgery_result',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('original_filename', sa.String(255)),
        sa.Column('forgery_result', sa.String(255))
    )

def downgrade():
    op.drop_table('forgery_result')
