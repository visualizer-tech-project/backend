from enum import Enum
from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.program import Program
    from app.models.course import Course
    from app.models.user_progress import UserProgress
    from app.models.career_track import CareerTrack

class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'
    TEACHER = 'teacher'

class User(BaseModel, table=True):
    __tablename__ = 'users'
    
    email: str = Field(unique=True, max_length=255, index=True)
    hashed_password: str
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole

    programs: List['Program'] = Relationship(back_populates='user')
    courses: List['Course'] = Relationship(back_populates='user')
    progress: List['UserProgress'] = Relationship(back_populates='user')
    career_tracks: List['CareerTrack'] = Relationship(back_populates='user')