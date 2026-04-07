from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, CheckConstraint, Relationship, UniqueConstraint
from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.course import Course


class PrerequisiteBase(BaseSchema):
    prerequisite_course_id: int = Field(foreign_key="courses.id", gt=0)


class Prerequisite(BaseSQLModel, table=True):
    __tablename__ = 'prerequisites'
    __table_args__ = (
        UniqueConstraint('course_id', 'prerequisite_course_id', name='uq_course_prerequisite'),
        CheckConstraint('course_id != prerequisite_course_id', name='ck_no_self_prerequisite'),
    )

    course_id: int = Field(foreign_key='courses.id', nullable=False, index=True)
    prerequisite_course_id: int = Field(foreign_key='courses.id', nullable=False, index=True)

    course: 'Course' = Relationship(
        back_populates='prerequisites',
        sa_relationship_kwargs={'foreign_keys': 'Prerequisite.course_id', 'viewonly': True},
    )
    prerequisite_course: 'Course' = Relationship(
        back_populates='prerequisite_for',
        sa_relationship_kwargs={'foreign_keys': 'Prerequisite.prerequisite_course_id', 'viewonly': True},
    )


class PrerequisiteCreate(PrerequisiteBase):
    pass

class PrerequisiteUpdate(BaseSchema):
    prerequisite_course_id: Optional[int] = Field(None, foreign_key="courses.id", gt=0)


class PrerequisitePublic(PrerequisiteBase, BaseModelSchema):
    course_id: int = Field(foreign_key="courses.id")
