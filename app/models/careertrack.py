from typing import TYPE_CHECKING, List

from sqlmodel import Column, Field, Relationship, Text, UniqueConstraint

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class CareerTrack(BaseModel, table=True):
    __tablename__ = 'career_tracks'

    title: str = Field(unique=True, index=True, max_length=255, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=True))
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)

    user: 'User' = Relationship(back_populates='career_tracks')
    courses: List['CareerTrackCourse'] = Relationship(
        back_populates='career_track',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'},
    )


class CareerTrackCourse(BaseModel, table=True):
    __tablename__ = 'career_track_courses'
    __table_args__ = (
        UniqueConstraint('career_track_id', 'course_id', name='uq_track_course'),
    )

    career_track_id: int = Field(
        foreign_key='career_tracks.id', nullable=False, index=True
    )
    course_id: int = Field(foreign_key='courses.id', nullable=False, index=True)
    order_index: int = Field(default=0, nullable=False)

    career_track: 'CareerTrack' = Relationship(back_populates='courses')
    course: 'Course' = Relationship(back_populates='career_track_courses')
