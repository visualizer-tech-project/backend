from typing import TYPE_CHECKING, List, Optional
from pydantic import computed_field, ConfigDict
from sqlmodel import Field, Column, Relationship, Text, UniqueConstraint

from app.core.constants import TITLE_FIELD_CONFIG
from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.course import Course, CoursePublic
    from app.models.user import User, UserPublic


class CareerTrackCourseBase(BaseSchema):
    career_track_id: int = Field(foreign_key='career_tracks.id')
    course_id: int = Field(foreign_key='courses.id')
    order_index: int


class CareerTrackBase(BaseSchema):
    title: Optional[str] = Field(None, **TITLE_FIELD_CONFIG)
    description: Optional[str] = Field(None)
    user_id: int = Field(foreign_key='users.id')


class CareerTrack(BaseSQLModel, CareerTrackBase, table=True):
    __tablename__ = 'career_tracks'

    user: 'User' = Relationship(back_populates='career_tracks')
    courses: List['CareerTrackCourse'] = Relationship(
        back_populates='career_track', cascade_delete=True
    )


class CareerTrackCourse(BaseSQLModel, CareerTrackCourseBase, table=True):
    __tablename__ = 'career_track_courses'
    __table_args__ = (
        UniqueConstraint('career_track_id', 'course_id', name='uq_track_course'),
    )

    career_track: 'CareerTrack' = Relationship(back_populates='courses')
    course: 'Course' = Relationship(back_populates='career_track_courses')


class CareerTrackCoursePublic(CareerTrackCourseBase, BaseModelSchema):
    pass


class CareerTrackCreate(CareerTrackBase):
    pass


class CareerTrackUpdate(CareerTrackBase):
    user_id: Optional[int] = Field(None, foreign_key='users.id')


class CareerTrackPublic(CareerTrackBase, BaseModelSchema):
    user: 'UserPublic'

    @computed_field
    @property
    def courses_count(self) -> int:
        return getattr(self, '_courses_count', 0)


class TrackCourseItem(BaseSchema):
    order_index: int
    course: 'CoursePublic'

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CareerTrackWithCourses(CareerTrackPublic):
    courses: List[TrackCourseItem] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)
