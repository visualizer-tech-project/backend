"""add_indexes_and_constraints_manually

Revision ID: ae5fccf7e1ba
Revises: abcaa15a7c9e
Create Date: 2026-03-18 13:30:00.000000

"""
from typing import Sequence, Union
from contextlib import suppress

from alembic import op
import sqlalchemy as sa

revision: str = 'ae5fccf7e1ba'
down_revision: Union[str, Sequence[str], None] = 'abcaa15a7c9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Индексы для внешних ключей
    op.create_index('ix_courses_program_id', 'courses', ['program_id'], unique=False)
    op.create_index('ix_courses_user_id', 'courses', ['user_id'], unique=False)
    
    op.create_index('ix_programs_user_id', 'programs', ['user_id'], unique=False)
    
    op.create_index('ix_career_tracks_user_id', 'career_tracks', ['user_id'], unique=False)
    
    op.create_index('ix_career_track_courses_career_track_id', 'career_track_courses', ['career_track_id'], unique=False)
    op.create_index('ix_career_track_courses_course_id', 'career_track_courses', ['course_id'], unique=False)
    
    op.create_index('ix_prerequisites_course_id', 'prerequisites', ['course_id'], unique=False)
    op.create_index('ix_prerequisites_prerequisite_course_id', 'prerequisites', ['prerequisite_course_id'], unique=False)
    
    op.create_index('ix_user_progress_user_id', 'user_progress', ['user_id'], unique=False)
    op.create_index('ix_user_progress_course_id', 'user_progress', ['course_id'], unique=False)
    
    # Уникальные ограничения
    with suppress(Exception):
        op.create_unique_constraint(
            'uq_career_track_courses',
            'career_track_courses',
            ['career_track_id', 'course_id']
        )
    
    with suppress(Exception):
        op.create_unique_constraint(
            'uq_prerequisites', 'prerequisites', ['course_id', 'prerequisite_course_id']
        )
    
    with suppress(Exception):
        op.create_unique_constraint(
            'uq_user_progress', 'user_progress', ['user_id', 'course_id']
        )
    
    # Проверочное ограничение
    with suppress(Exception):
        op.create_check_constraint(
            'ck_prerequisite_no_self',
            'prerequisites',
            'course_id != prerequisite_course_id'
        )


def downgrade() -> None:
    # Удаляем проверочное ограничение
    with suppress(Exception):
        op.drop_constraint('ck_prerequisite_no_self', 'prerequisites', type_='check')
    
    # Удаляем уникальные ограничения
    with suppress(Exception):
        op.drop_constraint('uq_user_progress', 'user_progress', type_='unique')
    
    with suppress(Exception):
        op.drop_constraint('uq_prerequisites', 'prerequisites', type_='unique')
    
    with suppress(Exception):
        op.drop_constraint('uq_career_track_courses', 'career_track_courses', type_='unique')
    
    # Удаляем индексы
    with suppress(Exception):
        op.drop_index('ix_user_progress_course_id', table_name='user_progress')
    
    with suppress(Exception):
        op.drop_index('ix_user_progress_user_id', table_name='user_progress')
    
    with suppress(Exception):
        op.drop_index('ix_prerequisites_prerequisite_course_id', table_name='prerequisites')
    
    with suppress(Exception):
        op.drop_index('ix_prerequisites_course_id', table_name='prerequisites')
    
    with suppress(Exception):
        op.drop_index('ix_career_track_courses_course_id', table_name='career_track_courses')
    
    with suppress(Exception):
        op.drop_index('ix_career_track_courses_career_track_id', table_name='career_track_courses')
    
    with suppress(Exception):
        op.drop_index('ix_career_tracks_user_id', table_name='career_tracks')
    
    with suppress(Exception):
        op.drop_index('ix_programs_user_id', table_name='programs')
    
    with suppress(Exception):
        op.drop_index('ix_courses_user_id', table_name='courses')
    
    with suppress(Exception):
        op.drop_index('ix_courses_program_id', table_name='courses')