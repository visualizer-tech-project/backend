from datetime import datetime
from typing import List, Optional

from pydantic import Field, computed_field

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


class UpdateCourseOrder(BaseSchema):
    """Схема для обновления порядка курса"""

    new_order_index: int = Field(..., ge=0, description='Новый порядковый номер')


class ReorderCourses(BaseSchema):
    """Схема для полной перестановки курсов"""

    course_ids: List[int] = Field(..., description='Список ID курсов в новом порядке')


class CareerTrackPublic(BaseModelSchema):
    """Публичная информация о карьерном треке"""

    title: str
    description: Optional[str] = None
    user_id: int
    _courses_count: int = 0

    @computed_field
    @property
    def courses_count(self) -> int:
        return self._courses_count

    model_config = {"from_attributes": True}


class CareerTrackCoursePublic(BaseModelSchema):
    """Публичная информация о связи трека с курсом"""

    career_track_id: int
    course_id: int
    order_index: int


class TrackCourseItem(BaseSchema):
    """Элемент курса в треке"""

    order_index: int
    course: CoursePublic


class CareerTrackWithCourses(CareerTrackPublic):
    """Карьерный трек с курсами"""

    courses: List[TrackCourseItem] = []


class TrackCompletionCourse(BaseSchema):
    """Статус прохождения курса в треке"""

    order_index: int
    course_id: int
    course_title: str
    status: str
    grade: Optional[int] = None
    completed_at: Optional[str] = None


class TrackCompletionStatus(BaseSchema):
    """Статус прохождения трека пользователем"""

    total_courses: int
    completed_courses: int
    in_progress_courses: int
    not_started_courses: int
    completion_percentage: float
    courses: List[TrackCompletionCourse] = []


class TrackWithCoursesCount(BaseSchema):
    """Трек с количеством курсов"""

    id: int
    title: str
    description: Optional[str] = None
    user_id: int
    courses_count: int
    created_at: datetime


class PopularTrack(BaseSchema):
    """Популярный трек"""

    track: CareerTrackPublic
    courses_count: int
