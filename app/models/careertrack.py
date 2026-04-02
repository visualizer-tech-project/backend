from typing import TYPE_CHECKING, List, Optional

from pydantic import Field, computed_field
from sqlmodel import Column, Relationship, Text, UniqueConstraint
from sqlmodel import Field as SQLField

from app.models.base import BaseModelSchema, BaseSchema, BaseSQLModel
from app.models.course import CoursePublic

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class CareerTrack(BaseSQLModel, table=True):
    __tablename__ = 'career_tracks'

    title: str = SQLField(unique=True, index=True, max_length=255, nullable=False)
    description: str = SQLField(sa_column=Column(Text, nullable=True))
    user_id: int = SQLField(foreign_key='users.id', nullable=False, index=True)

    user: 'User' = Relationship(back_populates='career_tracks')
    courses: List['CareerTrackCourse'] = Relationship(
        back_populates='career_track', cascade_delete=True
    )


class CareerTrackCourse(BaseSQLModel, table=True):
    __tablename__ = 'career_track_courses'
    __table_args__ = (
        UniqueConstraint('career_track_id', 'course_id', name='uq_track_course'),
    )

    career_track_id: int = SQLField(
        foreign_key='career_tracks.id', nullable=False, index=True
    )
    course_id: int = SQLField(foreign_key='courses.id', nullable=False, index=True)
    order_index: int = SQLField(default=0, nullable=False)

    career_track: 'CareerTrack' = Relationship(back_populates='courses')
    course: 'Course' = Relationship(back_populates='career_track_courses')


class CareerTrackCreate(BaseSchema):
    """Схема для создания карьерного трека"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class CareerTrackUpdate(BaseSchema):
    """Схема для обновления карьерного трека"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class AddCourseToTrack(BaseSchema):
    """Схема для добавления курса в трек"""

    course_id: int = Field(..., gt=0)
    order_index: int = Field(..., ge=0)


class UpdateCourseOrder(BaseSchema):
    """Схема для обновления порядка курса"""

    new_order_index: int = Field(..., ge=0)


class ReorderCourses(BaseSchema):
    """Схема для полной перестановки курсов"""

    course_ids: List[int]


class CareerTrackPublic(BaseModelSchema):
    """Публичная информация о карьерном треке"""

    title: str
    description: Optional[str] = None
    user_id: int

    @computed_field
    @property
    def courses_count(self) -> int:
        return getattr(self, '_courses_count', 0)


class CareerTrackCoursePublic(BaseModelSchema):
    """Публичная информация о связи трека с курсом"""

    career_track_id: int
    course_id: int
    order_index: int


class CareerTrackWithCourses(CareerTrackPublic):
    """Карьерный трек с курсами"""

    courses: List['TrackCourseItem'] = []


class TrackCourseItem(BaseSchema):
    """Элемент курса в треке"""

    order_index: int
    course: 'CoursePublic'


TrackCourseItem.model_rebuild()
CareerTrackWithCourses.model_rebuild()
