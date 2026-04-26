"""smtp

Revision ID: 408800112450
Revises: d5d7104854d6
Create Date: 2026-04-26 12:36:12.925571
"""

from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa


revision: str = '408800112450'
down_revision: Union[str, Sequence[str], None] = 'd5d7104854d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

account_status_enum = sa.Enum(
    'CREATED', 'CONFIRMED', 'BLOCKED',
    name='accountstatus'
)


def upgrade() -> None:
    """Upgrade schema."""

    account_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('subject', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('action', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    op.create_table(
        'refresh_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('jti', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_refresh_sessions_is_valid', 'refresh_sessions', ['is_valid'])
    op.create_index(op.f('ix_refresh_sessions_jti'), 'refresh_sessions', ['jti'], unique=True)
    op.create_index('ix_refresh_sessions_user_id', 'refresh_sessions', ['user_id'])

    op.create_table(
        'role_permission',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id']),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    op.create_table(
        'user_role',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    op.add_column(
        'users',
        sa.Column('status', account_status_enum, nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('users', 'status')

    op.drop_table('user_role')
    op.drop_table('role_permission')

    op.drop_index('ix_refresh_sessions_user_id', table_name='refresh_sessions')
    op.drop_index(op.f('ix_refresh_sessions_jti'), table_name='refresh_sessions')
    op.drop_index('ix_refresh_sessions_is_valid', table_name='refresh_sessions')
    op.drop_table('refresh_sessions')

    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')

    op.drop_table('permissions')

    account_status_enum.drop(op.get_bind(), checkfirst=True)