from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Column, Relationship, Text, UniqueConstraint

from app.core.constants import TITLE_FIELD_CONFIG
from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.careertrack import CareerTrackCourse
    from app.models.prerequisite import Prerequisite
    from app.models.program import Program
    from app.models.user import User
    from app.models.userprogress import UserProgress


class CourseType(str, Enum):
    REQUIRED = 'required'
    ELECTIVE = 'elective'


class CourseBase(BaseSchema):
    title: str = Field(
        index=True,
        nullable=False,
        **TITLE_FIELD_CONFIG
    )
    description: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    type: CourseType = Field(default=CourseType.REQUIRED, nullable=False)
    program_id: int = Field(foreign_key='programs.id', nullable=False, index=True)
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)


class Course(CourseBase, BaseSQLModel, table=True):
    __tablename__ = 'courses'
    __table_args__ = (
        UniqueConstraint('title', 'program_id', name='uq_course_title_program'),
    )

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


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseSchema):
    title: Optional[str] = Field(None, **TITLE_FIELD_CONFIG)
    description: Optional[str] = None
    type: Optional[CourseType] = None
    program_id: Optional[int] = Field(None, foreign_key='programs.id')
    user_id: Optional[int] = Field(None, foreign_key='users.id')


class CoursePublic(CourseBase, BaseModelSchema):
    pass
