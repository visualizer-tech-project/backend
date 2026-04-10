from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic.v1.generics import GenericModel
from sqlalchemy import func
from sqlmodel import Field, SQLModel

T = TypeVar('T', bound=SQLModel)


class BaseSQLModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'server_default': func.now(), 'nullable': False},
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            'onupdate': func.now(),
            'server_default': func.now(),
            'nullable': False,
        },
    )


class BaseSchema(SQLModel):
    class Config:
        from_attributes = True


class BaseModelSchema(BaseSchema, BaseSQLModel):
    pass


class PaginationInfo(SQLModel):
    page: int
    pages_num: int
    total: int


class ListResponse(GenericModel, Generic[T]):
    info: PaginationInfo
    items: list[T]

    class Config:
        arbitrary_types_allowed = True
