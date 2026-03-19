from typing import TYPE_CHECKING, List

from sqlmodel import Column, Field, Relationship, Text

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class Program(BaseModel, table=True):
    __tablename__ = 'programs'

    title: str = Field(unique=True, index=True, max_length=255, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=True))
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)

    user: 'User' = Relationship(back_populates='programs')
    courses: List['Course'] = Relationship(
        back_populates='program',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
