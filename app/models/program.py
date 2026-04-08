from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Column, Relationship, Text

from app.core.constants import TITLE_FIELD_CONFIG, TITLE_MAX_LENGTH
from app.models.base import BaseSQLModel, BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User, UserPublic


class ProgramBase(BaseSchema):
    title: Optional[str] = Field(None, **TITLE_FIELD_CONFIG)
    description: Optional[str] = None
    user_id: int = Field(foreign_key="users.id")


class ProgramBaseFields(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class Program(BaseSQLModel, ProgramBase, table=True):
    __tablename__ = 'programs'

    title: str = Field(unique=True, index=True, max_length=TITLE_MAX_LENGTH, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=True))
    user_id: int = Field(foreign_key='users.id', nullable=False, index=True)

    user: 'User' = Relationship(back_populates='programs')
    courses: List['Course'] = Relationship(back_populates='program', cascade_delete=True)


class ProgramCreate(ProgramBase):
    title: str = Field(..., **TITLE_FIELD_CONFIG)


class ProgramUpdate(ProgramBase):
    pass


class ProgramPublic(ProgramBase, BaseModelSchema):
    user: 'UserPublic'
