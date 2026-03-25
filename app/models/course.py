from typing import TYPE_CHECKING, List

from sqlmodel import Column, Field, Relationship, Text

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.careertrack import CareerTrackCourse
    from app.models.prerequisite import Prerequisite
    from app.models.program import Program
    from app.models.user import User
    from app.models.userprogress import UserProgress


class Course(BaseModel, table=True):
    __tablename__ = 'courses'

    title: str = Field(unique=True, index=True, max_length=255, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=True))
    program_id: int = Field(foreign_key='programs.id', nullable=False, index=True)
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)

    program: 'Program' = Relationship(back_populates='courses')
    user: 'User' = Relationship(back_populates='courses')

    prerequisites: List['Prerequisite'] = Relationship(
        back_populates='course',
        sa_relationship_kwargs={
            'foreign_keys': 'Prerequisite.course_id',
            'cascade': 'all, delete-orphan',
        },
    )

    prerequisite_for: List['Prerequisite'] = Relationship(
        back_populates='prerequisite_course',
        sa_relationship_kwargs={
            'foreign_keys': 'Prerequisite.prerequisite_course_id',
            'cascade': 'all, delete-orphan',
        },
    )

    career_track_courses: List['CareerTrackCourse'] = Relationship(
        back_populates='course',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'},
    )

    progress: List['UserProgress'] = Relationship(
        back_populates='course',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'},
    )
