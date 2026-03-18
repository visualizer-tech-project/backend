from typing import TYPE_CHECKING

from sqlmodel import CheckConstraint, Field, Relationship, UniqueConstraint

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.course import Course


class Prerequisite(BaseModel, table=True):
    __tablename__ = 'prerequisites'
    __table_args__ = (
        UniqueConstraint(
            'course_id', 'prerequisite_course_id', name='uq_course_prerequisite'
        ),
        CheckConstraint(
            'course_id != prerequisite_course_id', name='ck_no_self_prerequisite'
        ),
    )

    course_id: int = Field(foreign_key='courses.id', nullable=False, index=True)
    prerequisite_course_id: int = Field(
        foreign_key='courses.id', nullable=False, index=True
    )

    course: 'Course' = Relationship(
        back_populates='prerequisites',
        sa_relationship_kwargs={
            'foreign_keys': 'Prerequisite.course_id',
            'viewonly': True,
        },
    )

    prerequisite_course: 'Course' = Relationship(
        back_populates='prerequisite_for',
        sa_relationship_kwargs={
            'foreign_keys': 'Prerequisite.prerequisite_course_id',
            'viewonly': True,
        },
    )
