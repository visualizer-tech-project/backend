from typing import List, Optional

from pydantic import Field

from app.schemas.base import BaseModelSchema, BaseSchema
from app.schemas.course import CoursePublic


class CareerTrackCreate(BaseSchema):
    """Схема для создания карьерного трека"""

    title: str = Field(..., min_length=1, max_length=255, description='Название трека')
    description: Optional[str] = Field(None, description='Описание трека')


class CareerTrackUpdate(BaseSchema):
    """Схема для обновления карьерного трека"""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description='Название трека'
    )
    description: Optional[str] = Field(None, description='Описание трека')


class AddCourseToTrack(BaseSchema):
    """Схема для добавления курса в трек"""

    course_id: int = Field(..., gt=0, description='ID курса')
    order_index: int = Field(..., ge=0, description='Порядковый номер в треке')


class CareerTrackPublic(BaseModelSchema):
    """Публичная информация о карьерном треке"""

    title: str
    description: Optional[str] = None
    created_by: int


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
    course: CoursePublic


CareerTrackWithCourses.model_rebuild()
