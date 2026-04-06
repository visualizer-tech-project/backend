from typing import TYPE_CHECKING, List, Optional

from pydantic import computed_field
from sqlmodel import Column, Relationship, Text, UniqueConstraint
from sqlmodel import Field

from app.models.base import BaseModelSchema, BaseSchema, BaseSQLModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User, UserPublic
    from app.models.course import CoursePublic


class CareerTrack(BaseSQLModel, table=True):
    __tablename__ = 'career_tracks'

    title: str = Field(unique=True, index=True, max_length=255, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=True))
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)

    user: 'User' = Relationship(back_populates='career_tracks')
    courses: List['CareerTrackCourse'] = Relationship(back_populates='career_track', cascade_delete=True)


class CareerTrackCourse(BaseSQLModel, table=True):
    __tablename__ = 'career_track_courses'
    __table_args__ = (UniqueConstraint('career_track_id', 'course_id', name='uq_track_course'),)

    career_track_id: int = Field(foreign_key='career_tracks.id', nullable=False, index=True)
    course_id: int = Field(foreign_key='courses.id', nullable=False, index=True)
    order_index: int = Field(default=0, nullable=False)

    career_track: 'CareerTrack' = Relationship(back_populates='courses')
    course: 'Course' = Relationship(back_populates='career_track_courses')


class CareerTrackCreate(BaseSchema):
    """Схема для создания/обновления карьерного трека"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class CareerTrackUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class CareerTrackCoursePublic(BaseModelSchema):
    career_track_id: int
    course_id: int
    order_index: int


class CareerTrackPublic(BaseModelSchema):
    title: str
    description: Optional[str] = None
    user_id: int
    user: Optional['UserPublic'] = None

    @computed_field
    @property
    def courses_count(self) -> int:
        return getattr(self, '_courses_count', 0)


class TrackCourseItem(BaseSchema):
    order_index: int
    course: 'CoursePublic'


class CareerTrackWithCourses(CareerTrackPublic):
    courses: List[TrackCourseItem] = []
