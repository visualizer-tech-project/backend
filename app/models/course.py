from typing import List, TYPE_CHECKING
from sqlmodel import Column, Field, Relationship, Text

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.prerequisite import Prerequisite
    from app.models.career_track import CareerTrackCourse
    from app.models.user_progress import UserProgress
    from app.models.program import Program
    from app.models.user import User

class Course(BaseModel, table=True):
    __tablename__ = 'courses'

    title: str = Field(unique=True, max_length=255, index=True)
    description: str = Field(sa_column=Column(Text))
    program_id: int = Field(foreign_key='programs.id')
    user_id: int = Field(foreign_key='users.id')

    program: 'Program' = Relationship(back_populates='courses')
    user: 'User' = Relationship(back_populates='courses')
    prerequisites: List['Prerequisite'] = Relationship(back_populates='course')
    prerequisite_for: List['Prerequisite'] = Relationship(
        back_populates='prerequisite_course',
        sa_relationship_kwargs={'foreign_keys': 'Prerequisite.prerequisite_course_id'}
    )
    career_track_courses: List['CareerTrackCourse'] = Relationship(
        back_populates='course'
    )
    progress: List['UserProgress'] = Relationship(back_populates='course')