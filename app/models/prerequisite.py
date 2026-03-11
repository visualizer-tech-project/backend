from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.course import Course


class Prerequisite(BaseModel, table=True):
    __tablename__ = 'prerequisites'

    course_id: int = Field(foreign_key='courses.id')
    prerequisite_course_id: int = Field(foreign_key='courses.id')

    course: 'Course' = Relationship(
        back_populates='prerequisites',
        sa_relationship_kwargs={'foreign_keys': 'Prerequisite.course_id'}
    )
    prerequisite_course: 'Course' = Relationship(
        back_populates='prerequisite_for',
        sa_relationship_kwargs={'foreign_keys': 'Prerequisite.prerequisite_course_id'}
    )