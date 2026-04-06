from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from sqlmodel import Field, Column, Relationship, Text

from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User, UserPublic


class Program(BaseSQLModel, table=True):
    __tablename__ = 'programs'

    title: str = Field(unique=True, index=True, max_length=255, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=True))
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)

    user: 'User' = Relationship(back_populates='programs')
    courses: List['Course'] = Relationship(back_populates='program', cascade_delete=True)


class ProgramBase(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class ProgramCreate(ProgramBase):
    title: str = Field(..., min_length=1, max_length=255)


class ProgramUpdate(ProgramBase):
    pass


class ProgramPublic(BaseModelSchema):
    title: str
    description: Optional[str] = None
    user_id: int = Field(foreign_key="users.id")
    user: Optional['UserPublic'] = None
