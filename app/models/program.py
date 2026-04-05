from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, Relationship, Text
from sqlmodel import Field

from app.models.user import UserPublic
from app.models.base import BaseModelSchema, BaseSchema, BaseSQLModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class Program(BaseSQLModel, table=True):
    __tablename__ = 'programs'

    title: str = Field(unique=True, index=True, max_length=255, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=True))
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)

    user: 'User' = Relationship(back_populates='programs')
    courses: List['Course'] = Relationship(back_populates='program', cascade_delete=True)


class ProgramCreate(BaseSchema):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class ProgramUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class ProgramPublic(BaseModelSchema):
    title: str
    description: Optional[str] = None
    user: Optional[UserPublic] = None
    