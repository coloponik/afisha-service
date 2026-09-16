"""создание таблицы event_payment_activity

Revision ID: 0001
Revises: 
Create Date: 2026-09-15 20:36:43.690004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('event_payment_activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('batch_id', sa.String(length=36), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('payments_count', sa.Integer(), nullable=False),
    sa.Column('tickets_count', sa.Integer(), nullable=False),
    sa.Column('total_amount', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('event_payment_activity')
