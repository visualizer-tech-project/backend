from typing import TYPE_CHECKING, List, Optional

from pydantic import Field
from sqlmodel import Column, Relationship, Text
from sqlmodel import Field as SQLField

from app.models.base import BaseModelSchema, BaseSchema, BaseSQLModel

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class Program(BaseSQLModel, table=True):
    __tablename__ = 'programs'

    title: str = SQLField(unique=True, index=True, max_length=255, nullable=False)
    description: str = SQLField(sa_column=Column(Text, nullable=True))
    user_id: int = SQLField(foreign_key='users.id', nullable=False, index=True)

    user: 'User' = Relationship(back_populates='programs')
    courses: List['Course'] = Relationship(
        back_populates='program', cascade_delete=True
    )


class ProgramCreate(BaseSchema):
    """Схема для создания программы"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class ProgramUpdate(BaseSchema):
    """Схема для обновления программы"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)


class ProgramPublic(BaseModelSchema):
    """Публичная информация о программе (наследует id, created_at, updated_at)"""

    title: str
    description: Optional[str] = None
    user_id: int


class ProgramCopyRequest(BaseSchema):
    """Схема для копирования программы"""

    title: str = Field(..., min_length=1, max_length=255)
