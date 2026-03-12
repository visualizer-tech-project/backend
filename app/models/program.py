from typing import TYPE_CHECKING, List

from sqlmodel import Column, Field, Relationship, Text

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class Program(BaseModel, table=True):
    __tablename__ = 'programs'

    title: str = Field(unique=True, max_length=255, index=True)
    description: str = Field(sa_column=Column(Text))
    user_id: int = Field(foreign_key='users.id')

    user: 'User' = Relationship(back_populates='programs')
    courses: List['Course'] = Relationship(back_populates='program')
