from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Column, Relationship, Text

from app.core.constants import TITLE_FIELD_CONFIG, TITLE_MAX_LENGTH
from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User, UserPublic


class ProgramBase(BaseSchema):
    title: str = Field(unique=True, index=True, max_length=TITLE_MAX_LENGTH, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)


class Program(BaseSQLModel, ProgramBase, table=True):
    __tablename__ = 'programs'

    user: 'User' = Relationship(back_populates='programs')
    courses: List['Course'] = Relationship(back_populates='program', cascade_delete=True)


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(ProgramBase):
    pass


class ProgramPublic(ProgramBase, BaseModelSchema):
    user: 'UserPublic'
