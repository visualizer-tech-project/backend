from typing import List, TYPE_CHECKING
from sqlmodel import Column, Field, Relationship, Text

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User

class CareerTrack(BaseModel, table=True):
    __tablename__ = 'career_tracks'

    title: str = Field(unique=True, max_length=255, index=True)
    description: str = Field(sa_column=Column(Text))
    user_id: int = Field(foreign_key='users.id')

    user: 'User' = Relationship(back_populates='career_tracks')
    courses: List['CareerTrackCourse'] = Relationship(back_populates='career_track')


class CareerTrackCourse(BaseModel, table=True):
    __tablename__ = 'career_track_courses'

    career_track_id: int = Field(foreign_key='career_tracks.id')
    course_id: int = Field(foreign_key='courses.id')
    order_index: int = Field(default=0)

    career_track: 'CareerTrack' = Relationship(back_populates='courses')
    course: 'Course' = Relationship(back_populates='career_track_courses')