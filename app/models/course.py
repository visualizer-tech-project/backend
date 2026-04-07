from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Column, Relationship, Text

from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.careertrack import CareerTrackCourse
    from app.models.prerequisite import Prerequisite
    from app.models.program import Program, ProgramPublic
    from app.models.user import User, UserPublic
    from app.models.userprogress import UserProgress


class CourseType(str, Enum):
    REQUIRED = 'required'
    ELECTIVE = 'elective'


class CourseBase(BaseSchema):
    title: str
    description: Optional[str] = None
    type: CourseType
    program_id: int = Field(foreign_key="programs.id")
    user_id: int = Field(foreign_key="users.id")


class Course(BaseSQLModel, CourseBase, table=True):
    __tablename__ = 'courses'

    title: str = Field(unique=True, index=True, max_length=255, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=True))
    program_id: int = Field(foreign_key='programs.id', nullable=False, index=True)
    type: CourseType = Field(default=CourseType.REQUIRED, nullable=False)
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)

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
    title: str = Field(..., min_length=1, max_length=255)
    type: CourseType
    program_id: int = Field(foreign_key="programs.id", gt=0)


class CourseUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    type: Optional[CourseType] = None


class CoursePublic(CourseBase, BaseModelSchema):
    program: Optional['ProgramPublic'] = None
    user: Optional['UserPublic'] = None
