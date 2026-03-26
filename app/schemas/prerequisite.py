from pydantic import Field

from app.schemas.base import BaseModelSchema, BaseSchema


class PrerequisiteCreate(BaseSchema):
    """Схема для создания пререквизита"""

    prerequisite_course_id: int = Field(..., gt=0, description='ID курса-пререквизита')


class PrerequisitePublic(BaseModelSchema):
    """Публичная информация о пререквизите"""

    course_id: int
    prerequisite_course_id: int
