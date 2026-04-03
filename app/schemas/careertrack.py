from typing import List

from pydantic import Field

from app.models.base import BaseSchema


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