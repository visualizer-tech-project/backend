"""rename

Revision ID: 3069ce165f23
Revises: 7cc227fc6534
Create Date: 2026-04-02 18:18:21.390215

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '3069ce165f23'
down_revision: Union[str, Sequence[str], None] = '7cc227fc6534'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TYPE progressstatus AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED')"
    )
    op.add_column(
        'user_progress',
        sa.Column(
            'status_new',
            sa.Enum('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', name='progressstatus'),
            nullable=True,
        ),
    )
    op.execute('UPDATE user_progress SET status_new = status::text::progressstatus')
    op.drop_column('user_progress', 'status')
    op.alter_column(
        'user_progress', 'status_new', new_column_name='status', nullable=False
    )
    op.execute('DROP TYPE userprogressstatus')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "CREATE TYPE userprogressstatus AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED')"
    )
    op.add_column(
        'user_progress',
        sa.Column(
            'status_old',
            sa.Enum(
                'NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', name='userprogressstatus'
            ),
            nullable=True,
        ),
    )
    op.execute('UPDATE user_progress SET status_old = status::text::userprogressstatus')
    op.drop_column('user_progress', 'status')
    op.alter_column(
        'user_progress', 'status_old', new_column_name='status', nullable=False
    )
    op.execute('DROP TYPE progressstatus')
