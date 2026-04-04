from typing import List, Optional, Any
from pydantic import Field, computed_field
from app.models.base import BaseSchema
from app.models.course import CoursePublic


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


class TrackCourseItem(BaseSchema):
    career_track_course: Any = Field(..., exclude=True)

    @computed_field
    @property
    def order_index(self) -> int:
        return self.career_track_course.order_index

    @computed_field
    @property
    def course(self) -> CoursePublic:
        return CoursePublic.model_validate(self.career_track_course.course)