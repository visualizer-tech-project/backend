from datetime import datetime, timezone
from typing import Generic, TypeVar
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Field, SQLModel


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


class BaseModelSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


class PaginationInfo(SQLModel):
    page: int
    pages_num: int
    total: int


T = TypeVar('T')

class ListResponse(BaseModel, Generic[T]):
    info: PaginationInfo
    items: list[T]