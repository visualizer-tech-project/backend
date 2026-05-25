"""create email_notifications table

Revision ID: 9f1a2b3c4d5e
Revises: c56646c9f836
Create Date: 2026-05-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '9f1a2b3c4d5e'
down_revision: Union[str, Sequence[str], None] = 'c56646c9f836'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'email_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False
        ),
        sa.Column(
            'updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False
        ),
        sa.Column('code', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.Integer(), nullable=False),
        sa.Column('expired_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_email_notifications_code', 'email_notifications', ['code'], unique=True)
    op.create_index('ix_email_notifications_user_id', 'email_notifications', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_email_notifications_user_id', table_name='email_notifications')
    op.drop_index('ix_email_notifications_code', table_name='email_notifications')
    op.drop_table('email_notifications')