from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from pydantic import Field
from sqlmodel import Column, Relationship, Text
from sqlmodel import Field as SQLField

from app.models.base import BaseModelSchema, BaseSchema, BaseSQLModel

if TYPE_CHECKING:
    from app.models.careertrack import CareerTrackCourse
    from app.models.prerequisite import Prerequisite
    from app.models.program import Program
    from app.models.user import User
    from app.models.userprogress import UserProgress


class CourseType(str, Enum):
    """Тип курса"""

    REQUIRED = 'required'
    ELECTIVE = 'elective'


class Course(BaseSQLModel, table=True):
    __tablename__ = 'courses'

    title: str = SQLField(unique=True, index=True, max_length=255, nullable=False)
    description: str = SQLField(sa_column=Column(Text, nullable=True))
    program_id: int = SQLField(foreign_key='programs.id', nullable=False, index=True)
    type: CourseType = SQLField(default=CourseType.REQUIRED, nullable=False)
    user_id: int = SQLField(foreign_key='users.id', nullable=False, index=True)

    program: 'Program' = Relationship(back_populates='courses')
    user: 'User' = Relationship(back_populates='courses')
    prerequisites: List['Prerequisite'] = Relationship(
        back_populates='course',
        sa_relationship_kwargs={
            'foreign_keys': 'Prerequisite.course_id',
            'cascade': 'all, delete-orphan',
        },
    )
    prerequisite_for: List['Prerequisite'] = Relationship(
        back_populates='prerequisite_course',
        sa_relationship_kwargs={
            'foreign_keys': 'Prerequisite.prerequisite_course_id',
            'cascade': 'all, delete-orphan',
        },
    )
    career_track_courses: List['CareerTrackCourse'] = Relationship(
        back_populates='course', cascade_delete=True
    )
    progress: List['UserProgress'] = Relationship(
        back_populates='course', cascade_delete=True
    )


class CourseCreate(BaseSchema):
    """Схема для создания курса"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    type: CourseType
    program_id: int = Field(..., gt=0)


class CourseUpdate(BaseSchema):
    """Схема для обновления курса"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    type: Optional[CourseType] = Field(None)


class CoursePublic(BaseModelSchema):
    """Публичная информация о курсе"""

    title: str
    description: Optional[str] = None
    type: CourseType
    program_id: int
    user_id: int


class CourseWithPrerequisites(CoursePublic):
    """Курс с пререквизитами"""

    prerequisites: List['CoursePublic'] = []
    prerequisite_for: List['CoursePublic'] = []


CourseWithPrerequisites.model_rebuild()
