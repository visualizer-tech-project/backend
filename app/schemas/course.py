from enum import Enum
from typing import List, Optional

from pydantic import Field

from app.schemas.base import BaseModelSchema, BaseSchema


class CourseType(str, Enum):
    """Тип курса"""

    REQUIRED = 'required'
    ELECTIVE = 'elective'


class CourseCreate(BaseSchema):
    """Схема для создания курса"""

    title: str = Field(..., min_length=1, max_length=255, description='Название курса')
    description: Optional[str] = Field(None, description='Описание курса')
    type: CourseType = Field(..., description='Тип курса (required/elective)')
    semester: int = Field(..., ge=1, le=12, description='Семестр')
    program_id: int = Field(..., gt=0, description='ID программы')


class CourseUpdate(BaseSchema):
    """Схема для обновления курса"""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description='Название курса'
    )
    description: Optional[str] = Field(None, description='Описание курса')
    type: Optional[CourseType] = Field(None, description='Тип курса')


class CoursePublic(BaseModelSchema):
    """Публичная информация о курсе"""

    title: str
    description: Optional[str] = None
    type: CourseType
    program_id: int
    created_by: int = Field(alias='user_id')


class CourseWithPrerequisites(CoursePublic):
    """Курс с пререквизитами"""

    prerequisites: List['CoursePublic'] = []
    prerequisite_for: List['CoursePublic'] = []


CourseWithPrerequisites.model_rebuild()
